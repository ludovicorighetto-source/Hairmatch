"""
Profiles router – PROFILE-001 / PROFILE-002 / PROFILE-006.

Endpoints:
  PATCH /api/v1/profiles/me/salon          → update own salon profile
  PATCH /api/v1/profiles/me/professional   → update own professional profile
  GET   /api/v1/profiles/{user_id}         → public profile (any role)
"""

from __future__ import annotations

import uuid
from typing import Union

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profiles.schemas import (
    PublicProfessionalProfileResponse,
    PublicSalonProfileResponse,
    SalonProfileResponse,
    ProfessionalProfileResponse,
    UpdateProfessionalProfileRequest,
    UpdateSalonProfileRequest,
)
from app.api.v1.profiles.service import ProfileService
from app.dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _get_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(db=db)


# ── PATCH /me/salon ────────────────────────────────────────────────────────────

@router.patch(
    "/me/salon",
    response_model=SalonProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the authenticated salon's profile (partial update)",
)
async def update_salon_profile(
    payload: UpdateSalonProfileRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProfileService = Depends(_get_service),
) -> SalonProfileResponse:
    return await service.update_salon_profile(user_id, payload)


# ── PATCH /me/professional ─────────────────────────────────────────────────────

@router.patch(
    "/me/professional",
    response_model=ProfessionalProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the authenticated professional's profile (partial update)",
)
async def update_professional_profile(
    payload: UpdateProfessionalProfileRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProfileService = Depends(_get_service),
) -> ProfessionalProfileResponse:
    return await service.update_professional_profile(user_id, payload)


# ── GET /{user_id} ─────────────────────────────────────────────────────────────

@router.get(
    "/{user_id}",
    response_model=Union[PublicSalonProfileResponse, PublicProfessionalProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Get a public profile by user ID (no auth required)",
)
async def get_public_profile(
    user_id: uuid.UUID,
    service: ProfileService = Depends(_get_service),
) -> Union[PublicSalonProfileResponse, PublicProfessionalProfileResponse]:
    return await service.get_public_profile(user_id)
