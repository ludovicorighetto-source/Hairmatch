"""
Supabase Auth wrapper.

All calls use the Supabase REST Auth API via httpx so that we remain
framework-agnostic and avoid installing the heavy supabase-py SDK.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.core.exceptions import ExternalServiceError, InvalidCredentialsError, UserAlreadyExistsError

settings = get_settings()

_AUTH_BASE = f"{settings.SUPABASE_URL}/auth/v1"

# Common headers for admin (service-role) operations
_ADMIN_HEADERS = {
    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}

# Common headers for anonymous / user operations
_ANON_HEADERS = {
    "apikey": settings.SUPABASE_ANON_KEY,
    "Content-Type": "application/json",
}


def _user_headers(access_token: str) -> dict[str, str]:
    return {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


class SupabaseAuthClient:
    """Thin async wrapper around the Supabase Auth REST API."""

    # ── Sign up ────────────────────────────────────────────────────────────────

    async def sign_up(self, email: str, password: str) -> dict[str, Any]:
        """
        Create a new user in Supabase Auth.

        Returns the full Supabase response dict, which includes
        ``user.id``, ``session.access_token``, ``session.refresh_token``.

        Raises:
            UserAlreadyExistsError: if the email is already registered.
            ExternalServiceError: for any other Supabase error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_AUTH_BASE}/signup",
                headers=_ANON_HEADERS,
                json={"email": email, "password": password},
                timeout=10.0,
            )

        if resp.status_code == 422:
            body = resp.json()
            msg = body.get("msg") or body.get("message") or str(body)
            if "already" in msg.lower() or "exists" in msg.lower():
                raise UserAlreadyExistsError()
            raise ExternalServiceError(f"Supabase signup error: {msg}")

        if resp.status_code not in (200, 201):
            body = resp.json()
            error_msg = body.get("error_description") or body.get("msg") or str(body)
            # Supabase returns 400 for "User already registered"
            if resp.status_code == 400 and (
                "already registered" in str(error_msg).lower()
                or "already exists" in str(error_msg).lower()
            ):
                raise UserAlreadyExistsError()
            raise ExternalServiceError(f"Supabase signup failed: {error_msg}")

        return resp.json()

    # ── Sign in ────────────────────────────────────────────────────────────────

    async def sign_in_with_password(self, email: str, password: str) -> dict[str, Any]:
        """
        Authenticate with email + password.

        Returns the full Supabase session dict.

        Raises:
            InvalidCredentialsError: if the credentials are wrong.
            ExternalServiceError: for any other Supabase error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_AUTH_BASE}/token?grant_type=password",
                headers=_ANON_HEADERS,
                json={"email": email, "password": password},
                timeout=10.0,
            )

        if resp.status_code == 400:
            body = resp.json()
            error = body.get("error") or body.get("error_description") or ""
            if "invalid" in str(error).lower() or "credentials" in str(error).lower():
                raise InvalidCredentialsError()
            raise InvalidCredentialsError()

        if resp.status_code != 200:
            body = resp.json()
            raise ExternalServiceError(
                f"Supabase sign-in failed ({resp.status_code}): {body}"
            )

        return resp.json()

    # ── Sign out ───────────────────────────────────────────────────────────────

    async def sign_out(self, access_token: str) -> None:
        """
        Invalidate the access token on the Supabase side.

        Supabase returns 204 on success; we ignore non-critical errors.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_AUTH_BASE}/logout",
                headers=_user_headers(access_token),
                timeout=10.0,
            )
        # 204 = success; 401 = already expired – both are acceptable
        if resp.status_code not in (200, 204, 401):
            raise ExternalServiceError(f"Supabase sign-out failed ({resp.status_code})")

    # ── Refresh token ──────────────────────────────────────────────────────────

    async def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        """
        Exchange a refresh token for a new session.

        Returns a new session dict with ``access_token`` and ``refresh_token``.

        Raises:
            ExternalServiceError: if Supabase refuses the refresh token.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_AUTH_BASE}/token?grant_type=refresh_token",
                headers=_ANON_HEADERS,
                json={"refresh_token": refresh_token},
                timeout=10.0,
            )

        if resp.status_code != 200:
            body = resp.json()
            raise ExternalServiceError(
                f"Supabase token refresh failed ({resp.status_code}): {body}"
            )

        return resp.json()

    # ── Delete user (admin) ────────────────────────────────────────────────────

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """
        Hard-delete a user from Supabase Auth (used for rollback on registration failure).

        Uses the service-role key (admin endpoint).
        """
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{_AUTH_BASE}/admin/users/{user_id}",
                headers=_ADMIN_HEADERS,
                timeout=10.0,
            )
        # 200 or 404 are both fine for a rollback operation
        if resp.status_code not in (200, 204, 404):
            # Log but don't raise – we're already in a rollback path
            import logging

            logging.getLogger(__name__).error(
                "Failed to delete Supabase user %s during rollback: HTTP %s",
                user_id,
                resp.status_code,
            )

    # ── Get user (admin) ───────────────────────────────────────────────────────

    async def get_user(self, user_id: uuid.UUID) -> Optional[dict[str, Any]]:
        """Retrieve a Supabase user record by ID using the admin API."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_AUTH_BASE}/admin/users/{user_id}",
                headers=_ADMIN_HEADERS,
                timeout=10.0,
            )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise ExternalServiceError(
                f"Supabase get_user failed ({resp.status_code}): {resp.text}"
            )
        return resp.json()


# Module-level singleton so it can be imported directly
supabase_auth = SupabaseAuthClient()
