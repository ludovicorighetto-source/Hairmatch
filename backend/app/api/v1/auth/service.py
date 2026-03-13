"""
Auth service – all business logic for registration, login, logout,
token refresh, and current-user retrieval.

Pattern: SupabaseClient → Service → Router
"""

from __future__ import annotations

import logging
import uuid
from typing import Union

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.schemas import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MeResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterProfessionalRequest,
    RegisterProfessionalResponse,
    RegisterSalonRequest,
    RegisterSalonResponse,
    RequestPasswordResetRequest,
    RequestPasswordResetResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenPair,
)
from app.api.v1.auth.supabase_client import SupabaseAuthClient
from app.config import get_settings
from app.core.exceptions import (
    DatabaseError,
    ExternalServiceError,
    InactiveUserError,
    RefreshTokenError,
    UserNotFoundError,
)
from app.core.security import (
    extract_user_id_from_token,
    make_redis_refresh_key,
    verify_supabase_jwt,
)
from app.models.enums import UserRole
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile
from app.models.user_profile import UserProfile

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Orchestrates Supabase Auth + PostgreSQL for all auth operations."""

    def __init__(
        self,
        db: AsyncSession,
        redis_client: aioredis.Redis,
        supabase: SupabaseAuthClient,
    ) -> None:
        self._db = db
        self._redis = redis_client
        self._supabase = supabase

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _build_token_pair(self, supabase_session: dict) -> TokenPair:
        """Extract token information from a Supabase session dict."""
        return TokenPair(
            access_token=supabase_session["access_token"],
            refresh_token=supabase_session["refresh_token"],
            expires_in=supabase_session.get("expires_in", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        )

    async def _store_refresh_token(self, user_id: uuid.UUID, refresh_token: str) -> None:
        """Persist the refresh token in Redis with a 7-day TTL."""
        key = make_redis_refresh_key(user_id, refresh_token)
        await self._redis.setex(key, settings.refresh_token_expire_seconds, refresh_token)

    async def _revoke_refresh_token(self, user_id: uuid.UUID, refresh_token: str) -> None:
        """Remove a refresh token from Redis (rotation / logout)."""
        key = make_redis_refresh_key(user_id, refresh_token)
        await self._redis.delete(key)

    async def _validate_refresh_token_in_redis(
        self, user_id: uuid.UUID, refresh_token: str
    ) -> None:
        """
        Ensure the refresh token is present in Redis.

        Raises RefreshTokenError if not found.
        """
        key = make_redis_refresh_key(user_id, refresh_token)
        stored = await self._redis.get(key)
        if stored is None:
            raise RefreshTokenError("Refresh token not found or expired")

    async def _get_user_with_profile(
        self, user_id: uuid.UUID
    ) -> tuple[UserProfile, Union[SalonProfile, ProfessionalProfile]]:
        """
        Load UserProfile + the role-specific profile from the DB.

        Raises:
            UserNotFoundError: if the user_profile row is missing.
            DatabaseError: if the profile row is missing (data inconsistency).
        """
        user_result = await self._db.execute(
            select(UserProfile).where(UserProfile.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()

        if user.role == UserRole.salon:
            profile_result = await self._db.execute(
                select(SalonProfile).where(SalonProfile.user_id == user_id)
            )
            profile = profile_result.scalar_one_or_none()
        else:
            profile_result = await self._db.execute(
                select(ProfessionalProfile).where(ProfessionalProfile.user_id == user_id)
            )
            profile = profile_result.scalar_one_or_none()

        if profile is None:
            raise DatabaseError("User profile data is inconsistent – profile row missing")

        return user, profile

    # ── Register Salon ─────────────────────────────────────────────────────────

    async def register_salon(self, payload: RegisterSalonRequest) -> RegisterSalonResponse:
        """
        1. Create Supabase Auth user.
        2. Insert user_profiles row.
        3. Insert salon_profiles row.
        4. Store refresh token in Redis.
        5. Rollback Supabase user if DB insert fails.
        """
        supabase_resp = await self._supabase.sign_up(payload.email, payload.password)

        supabase_user = supabase_resp.get("user") or supabase_resp
        supabase_user_id = uuid.UUID(supabase_user["id"])

        try:
            user = UserProfile(
                id=supabase_user_id,
                role=UserRole.salon,
                is_active=True,
                is_verified=False,
            )
            self._db.add(user)
            await self._db.flush()

            salon = SalonProfile(
                user_id=supabase_user_id,
                business_name=payload.business_name,
                phone=payload.phone,
                vat_number=payload.vat_number,
                website_url=payload.website_url,
                address_street=payload.address.street,
                address_city=payload.address.city,
                address_province=payload.address.province,
                address_postal_code=payload.address.postal_code,
                address_country=payload.address.country,
            )
            self._db.add(salon)
            await self._db.flush()
            await self._db.refresh(user)
            await self._db.refresh(salon)

        except Exception as exc:
            logger.error("DB insert failed during salon registration, rolling back Supabase user %s: %s", supabase_user_id, exc)
            await self._supabase.delete_user(supabase_user_id)
            raise DatabaseError("Registration failed – could not persist user data") from exc

        # Store refresh token if a session was returned (email confirmation disabled)
        session = supabase_resp.get("session")
        if session and session.get("refresh_token"):
            await self._store_refresh_token(supabase_user_id, session["refresh_token"])

        return RegisterSalonResponse(
            user=user,  # type: ignore[arg-type]
            profile=salon,  # type: ignore[arg-type]
        )

    # ── Register Professional ──────────────────────────────────────────────────

    async def register_professional(
        self, payload: RegisterProfessionalRequest
    ) -> RegisterProfessionalResponse:
        """
        1. Create Supabase Auth user.
        2. Insert user_profiles row.
        3. Insert professional_profiles row.
        4. Store refresh token in Redis.
        5. Rollback Supabase user if DB insert fails.
        """
        supabase_resp = await self._supabase.sign_up(payload.email, payload.password)

        supabase_user = supabase_resp.get("user") or supabase_resp
        supabase_user_id = uuid.UUID(supabase_user["id"])

        try:
            user = UserProfile(
                id=supabase_user_id,
                role=UserRole.professional,
                is_active=True,
                is_verified=False,
            )
            self._db.add(user)
            await self._db.flush()

            professional = ProfessionalProfile(
                user_id=supabase_user_id,
                first_name=payload.first_name,
                last_name=payload.last_name,
                phone=payload.phone,
                date_of_birth=payload.date_of_birth,
                specializations=payload.specializations,
                years_of_experience=payload.years_of_experience,
                preferred_city=payload.preferred_city,
                preferred_province=payload.preferred_province,
            )
            self._db.add(professional)
            await self._db.flush()
            await self._db.refresh(user)
            await self._db.refresh(professional)

        except Exception as exc:
            logger.error(
                "DB insert failed during professional registration, rolling back Supabase user %s: %s",
                supabase_user_id,
                exc,
            )
            await self._supabase.delete_user(supabase_user_id)
            raise DatabaseError("Registration failed – could not persist user data") from exc

        session = supabase_resp.get("session")
        if session and session.get("refresh_token"):
            await self._store_refresh_token(supabase_user_id, session["refresh_token"])

        return RegisterProfessionalResponse(
            user=user,  # type: ignore[arg-type]
            profile=professional,  # type: ignore[arg-type]
        )

    # ── Login ──────────────────────────────────────────────────────────────────

    async def login(self, payload: LoginRequest) -> LoginResponse:
        """
        Authenticate user and return tokens + profile.

        1. Call Supabase sign-in.
        2. Decode JWT to get user_id.
        3. Load profile from DB.
        4. Store refresh token in Redis.
        5. Return token pair + profile.
        """
        session = await self._supabase.sign_in_with_password(payload.email, payload.password)

        access_token: str = session["access_token"]
        refresh_token: str = session["refresh_token"]

        user_id = extract_user_id_from_token(access_token)
        user, profile = await self._get_user_with_profile(user_id)

        if not user.is_active:
            raise InactiveUserError()

        await self._store_refresh_token(user_id, refresh_token)

        token_pair = self._build_token_pair(session)

        return LoginResponse(
            tokens=token_pair,
            user=user,  # type: ignore[arg-type]
            profile=profile,  # type: ignore[arg-type]
        )

    # ── Logout ─────────────────────────────────────────────────────────────────

    async def logout(
        self, access_token: str, refresh_token: str | None = None
    ) -> LogoutResponse:
        """
        1. Revoke access token on Supabase.
        2. Delete refresh token from Redis (if provided).
        """
        user_id: uuid.UUID | None = None
        try:
            user_id = extract_user_id_from_token(access_token)
        except Exception:
            pass  # Token may already be expired; still attempt sign-out

        await self._supabase.sign_out(access_token)

        if user_id and refresh_token:
            await self._revoke_refresh_token(user_id, refresh_token)

        return LogoutResponse()

    # ── Refresh ────────────────────────────────────────────────────────────────

    async def refresh(self, payload: RefreshRequest) -> RefreshResponse:
        """
        Token rotation:
        1. Decode old access token to get user_id (may be expired – we only need sub).
        2. Validate old refresh token exists in Redis.
        3. Exchange with Supabase for new token pair.
        4. Delete old Redis entry, store new one.
        5. Return new token pair.
        """
        # Decode without expiry check to extract user_id
        from jose import jwt as jose_jwt
        from jose.exceptions import JWTError

        # We use the refresh token itself to fetch the new session from Supabase first,
        # then derive the user_id from the new access token.
        new_session = await self._supabase.refresh_session(payload.refresh_token)

        new_access_token: str = new_session["access_token"]
        new_refresh_token: str = new_session["refresh_token"]

        user_id = extract_user_id_from_token(new_access_token)

        # Validate the OLD refresh token is still in Redis (replay-attack protection)
        await self._validate_refresh_token_in_redis(user_id, payload.refresh_token)

        # Rotate: remove old, store new
        await self._revoke_refresh_token(user_id, payload.refresh_token)
        await self._store_refresh_token(user_id, new_refresh_token)

        token_pair = self._build_token_pair(new_session)
        return RefreshResponse(tokens=token_pair)

    # ── Me ─────────────────────────────────────────────────────────────────────

    async def get_current_user_profile(self, user_id: uuid.UUID) -> MeResponse:
        """Load the current user + role-specific profile."""
        user, profile = await self._get_user_with_profile(user_id)

        if not user.is_active:
            raise InactiveUserError()

        return MeResponse(
            user=user,  # type: ignore[arg-type]
            profile=profile,  # type: ignore[arg-type]
        )

    # ── Resend Verification (AUTH-002) ─────────────────────────────────────────

    async def resend_verification(
        self, payload: ResendVerificationRequest
    ) -> ResendVerificationResponse:
        """
        Re-send the email confirmation link via Supabase.

        Always returns a generic success message to prevent user enumeration.
        """
        try:
            await self._supabase.resend_verification_email(payload.email)
        except ExternalServiceError as exc:
            logger.warning("resend_verification: Supabase error for %s: %s", payload.email, exc)
            # Do not surface the error to the client – return generic success
        return ResendVerificationResponse()

    # ── Request Password Reset (AUTH-003) ──────────────────────────────────────

    async def request_password_reset(
        self, payload: RequestPasswordResetRequest
    ) -> RequestPasswordResetResponse:
        """
        Trigger a Supabase password-reset email.

        Always returns a generic success to prevent user enumeration.
        """
        try:
            await self._supabase.send_password_reset_email(payload.email)
        except ExternalServiceError as exc:
            logger.warning("request_password_reset: Supabase error for %s: %s", payload.email, exc)
        return RequestPasswordResetResponse()

    # ── Reset Password (AUTH-003) ──────────────────────────────────────────────

    async def reset_password(self, payload: ResetPasswordRequest) -> ResetPasswordResponse:
        """
        Update the user's password using the recovery access token from Supabase.
        """
        await self._supabase.update_user_password(payload.access_token, payload.new_password)
        return ResetPasswordResponse()
