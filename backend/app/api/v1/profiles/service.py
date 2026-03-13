"""
Profile service – business logic for PROFILE-001 / PROFILE-002.

Handles partial updates of salon and professional profiles.
"""

from __future__ import annotations

import logging
import uuid
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.profiles.schemas import (
    PublicProfessionalProfileResponse,
    PublicSalonProfileResponse,
    SalonProfileResponse,
    ProfessionalProfileResponse,
    UpdateProfessionalProfileRequest,
    UpdateSalonProfileRequest,
)
from app.core.exceptions import DatabaseError, PermissionDeniedError, UserNotFoundError
from app.models.enums import UserRole
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile
from app.models.user_profile import UserProfile

logger = logging.getLogger(__name__)


# ── Completion checkers ────────────────────────────────────────────────────────

_SALON_REQUIRED = {
    "business_name", "phone", "address_street", "address_city",
    "address_province", "address_postal_code",
}

_PROFESSIONAL_REQUIRED = {
    "first_name", "last_name", "phone",
}


def _is_salon_complete(salon: SalonProfile) -> bool:
    return all(getattr(salon, f) for f in _SALON_REQUIRED) and bool(salon.description)


def _is_professional_complete(pro: ProfessionalProfile) -> bool:
    return (
        all(getattr(pro, f) for f in _PROFESSIONAL_REQUIRED)
        and bool(pro.bio)
        and bool(pro.specializations)
    )


# ── Service ────────────────────────────────────────────────────────────────────

class ProfileService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _get_user(self, user_id: uuid.UUID) -> UserProfile:
        result = await self._db.execute(
            select(UserProfile).where(UserProfile.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        return user

    async def _get_salon(self, user_id: uuid.UUID) -> SalonProfile:
        result = await self._db.execute(
            select(SalonProfile).where(SalonProfile.user_id == user_id)
        )
        salon = result.scalar_one_or_none()
        if salon is None:
            raise DatabaseError("Salon profile not found")
        return salon

    async def _get_professional(self, user_id: uuid.UUID) -> ProfessionalProfile:
        result = await self._db.execute(
            select(ProfessionalProfile).where(ProfessionalProfile.user_id == user_id)
        )
        pro = result.scalar_one_or_none()
        if pro is None:
            raise DatabaseError("Professional profile not found")
        return pro

    # ── PATCH /profiles/me/salon (PROFILE-001) ────────────────────────────────

    async def update_salon_profile(
        self, user_id: uuid.UUID, payload: UpdateSalonProfileRequest
    ) -> SalonProfileResponse:
        user = await self._get_user(user_id)
        if user.role != UserRole.salon:
            raise PermissionDeniedError("This endpoint is only for salon accounts")

        salon = await self._get_salon(user_id)

        # Apply only provided (non-None) fields
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(salon, field, value)

        salon.is_profile_complete = _is_salon_complete(salon)

        await self._db.flush()
        await self._db.refresh(salon)

        logger.info("Salon profile updated for user %s (complete=%s)", user_id, salon.is_profile_complete)
        return SalonProfileResponse.model_validate(salon)

    # ── PATCH /profiles/me/professional (PROFILE-002) ─────────────────────────

    async def update_professional_profile(
        self, user_id: uuid.UUID, payload: UpdateProfessionalProfileRequest
    ) -> ProfessionalProfileResponse:
        user = await self._get_user(user_id)
        if user.role != UserRole.professional:
            raise PermissionDeniedError("This endpoint is only for professional accounts")

        pro = await self._get_professional(user_id)

        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(pro, field, value)

        pro.is_profile_complete = _is_professional_complete(pro)

        await self._db.flush()
        await self._db.refresh(pro)

        logger.info("Professional profile updated for user %s (complete=%s)", user_id, pro.is_profile_complete)
        return ProfessionalProfileResponse.model_validate(pro)

    # ── GET /profiles/{user_id} (PROFILE-006) ────────────────────────────────

    async def get_public_profile(
        self, user_id: uuid.UUID
    ) -> Union[PublicSalonProfileResponse, PublicProfessionalProfileResponse]:
        user = await self._get_user(user_id)

        if user.role == UserRole.salon:
            salon = await self._get_salon(user_id)
            from app.api.v1.profiles.schemas import PublicUserResponse  # noqa: PLC0415
            return PublicSalonProfileResponse(
                user=PublicUserResponse.model_validate(user),
                profile=SalonProfileResponse.model_validate(salon),
            )
        else:
            pro = await self._get_professional(user_id)
            from app.api.v1.profiles.schemas import PublicUserResponse  # noqa: PLC0415
            return PublicProfessionalProfileResponse(
                user=PublicUserResponse.model_validate(user),
                profile=ProfessionalProfileResponse.model_validate(pro),
            )
