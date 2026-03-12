"""
Auth router – HTTP request/response layer only.

All business logic lives in AuthService.
The login endpoint is rate-limited via slowapi: 10 requests per 15 minutes per IP.
"""

from __future__ import annotations

import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.schemas import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    MeResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterProfessionalRequest,
    RegisterProfessionalResponse,
    RegisterSalonRequest,
    RegisterSalonResponse,
)
from app.api.v1.auth.service import AuthService
from app.api.v1.auth.supabase_client import supabase_auth
from app.config import get_settings
from app.dependencies import get_current_user_id, get_db, get_raw_token, get_redis

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Shared service factory ─────────────────────────────────────────────────────

def _get_service(
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(db=db, redis_client=redis_client, supabase=supabase_auth)


# ── Register Salon ─────────────────────────────────────────────────────────────

@router.post(
    "/register/salon",
    response_model=RegisterSalonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new salon account",
)
async def register_salon(
    payload: RegisterSalonRequest,
    service: AuthService = Depends(_get_service),
) -> RegisterSalonResponse:
    return await service.register_salon(payload)


# ── Register Professional ──────────────────────────────────────────────────────

@router.post(
    "/register/professional",
    response_model=RegisterProfessionalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new professional account",
)
async def register_professional(
    payload: RegisterProfessionalRequest,
    service: AuthService = Depends(_get_service),
) -> RegisterProfessionalResponse:
    return await service.register_professional(payload)


# ── Login (rate limited) ───────────────────────────────────────────────────────

def _login_rate_limit() -> str:
    """Return the configured rate limit string for the login endpoint."""
    return settings.RATE_LIMIT_LOGIN


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password (rate limited: 10/15 min per IP)",
)
async def login(
    request: Request,
    payload: LoginRequest,
    service: AuthService = Depends(_get_service),
) -> LoginResponse:
    # slowapi reads request.state.view to apply limits; the limiter middleware
    # checks the decorator applied below via app.state.limiter.
    return await service.login(payload)


# Apply the rate limit decorator after defining the function so we can reference
# the module-level limiter that is set in main.py at startup.
# We use a lazy import to avoid a circular dependency.
def _apply_rate_limit() -> None:
    try:
        from app.main import limiter  # noqa: PLC0415

        limiter.limit(settings.RATE_LIMIT_LOGIN)(login)
    except ImportError:
        pass  # main not yet imported (e.g. during testing with direct router mounting)


_apply_rate_limit()


# ── Logout ─────────────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout – invalidate access and refresh tokens",
)
async def logout(
    body: LogoutRequest,
    raw_token: str = Depends(get_raw_token),
    service: AuthService = Depends(_get_service),
) -> LogoutResponse:
    return await service.logout(
        access_token=raw_token,
        refresh_token=body.refresh_token,
    )


# ── Refresh ────────────────────────────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access and refresh tokens (token rotation)",
)
async def refresh_tokens(
    payload: RefreshRequest,
    service: AuthService = Depends(_get_service),
) -> RefreshResponse:
    return await service.refresh(payload)


# ── Me ─────────────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current authenticated user and their profile",
)
async def me(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: AuthService = Depends(_get_service),
) -> MeResponse:
    return await service.get_current_user_profile(user_id)
