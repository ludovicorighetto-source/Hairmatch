"""
Matching router – MATCH-002 / MATCH-003.

GET /api/v1/matching/professionals   → ranked professionals for the authenticated salon
GET /api/v1/matching/jobs            → ranked job postings for the authenticated professional
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.matching.schemas import MatchedJob, MatchedProfessional
from app.api.v1.matching.service import MatchingService
from app.core.exceptions import PermissionDeniedError
from app.dependencies import get_current_user_id, get_db
from app.models.enums import UserRole
from app.models.user_profile import UserProfile
from sqlalchemy import select

router = APIRouter(prefix="/matching", tags=["matching"])


async def _get_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise PermissionDeniedError("User not found")
    return user


def _get_service(db: AsyncSession = Depends(get_db)) -> MatchingService:
    return MatchingService(db)


# ── MATCH-002: Top professionals for salon ────────────────────────────────────

@router.get(
    "/professionals",
    response_model=List[MatchedProfessional],
    summary="Top matching professionals for the authenticated salon",
)
async def top_professionals(
    specializations: Optional[List[str]] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    user: UserProfile = Depends(_get_user),
    service: MatchingService = Depends(_get_service),
) -> List[MatchedProfessional]:
    if user.role != UserRole.salon:
        raise PermissionDeniedError("Only salons can access this endpoint")
    return await service.top_professionals_for_salon(
        salon_user_id=user.id,
        wanted_specializations=specializations,
        limit=limit,
    )


# ── MATCH-003: Recommended jobs for professional ──────────────────────────────

@router.get(
    "/jobs",
    response_model=List[MatchedJob],
    summary="Recommended job postings for the authenticated professional",
)
async def recommended_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    user: UserProfile = Depends(_get_user),
    service: MatchingService = Depends(_get_service),
) -> List[MatchedJob]:
    if user.role != UserRole.professional:
        raise PermissionDeniedError("Only professionals can access this endpoint")
    return await service.recommended_jobs_for_professional(
        professional_user_id=user.id,
        limit=limit,
    )
