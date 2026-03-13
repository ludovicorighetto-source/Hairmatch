"""
Matching service – MATCH-001 / MATCH-002 / MATCH-003.

Scoring formula (pure Python, no ML needed for MVP):

  For salon → professionals:
    score = 0.40 * specialization_overlap
          + 0.30 * location_match
          + 0.20 * experience_score
          + 0.10 * availability_score

  For professional → jobs:
    score = 0.50 * specialization_overlap
          + 0.30 * location_match
          + 0.20 * contract_type_match
"""

from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.matching.schemas import (
    JobScoreBreakdown,
    MatchedJob,
    MatchedProfessional,
    ScoreBreakdown,
)
from app.models.enums import AvailabilityStatus, JobStatus
from app.models.job_posting import JobPosting
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile

logger = logging.getLogger(__name__)


# ── Score helpers ─────────────────────────────────────────────────────────────


def _specialization_score(set_a: list[str], set_b: list[str]) -> float:
    """Jaccard-like overlap: |intersection| / |union|. Returns 0 if both empty."""
    a = {s.lower() for s in set_a}
    b = {s.lower() for s in set_b}
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _location_score(
    city_a: Optional[str],
    province_a: Optional[str],
    city_b: Optional[str],
    province_b: Optional[str],
) -> float:
    """1.0 if same city, 0.6 if same province, 0.0 otherwise."""
    if city_a and city_b and city_a.lower() == city_b.lower():
        return 1.0
    if province_a and province_b and province_a.lower() == province_b.lower():
        return 0.6
    return 0.0


def _experience_score(years: Optional[int]) -> float:
    """Scale years 0–10+ to 0–1."""
    if years is None:
        return 0.0
    return min(years / 10.0, 1.0)


def _availability_score(status: AvailabilityStatus) -> float:
    mapping = {
        AvailabilityStatus.available: 1.0,
        AvailabilityStatus.partially_available: 0.5,
        AvailabilityStatus.not_available: 0.0,
        AvailabilityStatus.on_leave: 0.0,
    }
    return mapping.get(status, 0.0)


def _contract_type_score(
    preferred: list[str], offered: list[str]
) -> float:
    """Proportion of preferred contract types present in offered."""
    if not preferred:
        return 0.5  # no preference → neutral
    matches = sum(1 for p in preferred if p in offered)
    return matches / len(preferred)


# ── Service ───────────────────────────────────────────────────────────────────


class MatchingService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── MATCH-002: Top professionals for a salon ───────────────────────────────

    async def top_professionals_for_salon(
        self,
        salon_user_id,
        wanted_specializations: Optional[List[str]] = None,
        limit: int = 20,
    ) -> list[MatchedProfessional]:
        """
        Return up to `limit` professionals ranked by match score against the
        salon identified by `salon_user_id`.

        If `wanted_specializations` is provided it overrides the salon's own
        specialization needs (useful when the salon wants to match against a
        specific job posting).
        """
        # Load salon for location
        salon_stmt = select(SalonProfile).where(SalonProfile.user_id == salon_user_id)
        salon_result = await self._db.execute(salon_stmt)
        salon = salon_result.scalar_one_or_none()

        salon_city = salon.address_city if salon else None
        salon_province = salon.address_province if salon else None
        salon_specs: list[str] = wanted_specializations or []

        # Load all complete, non-unavailable professionals
        prof_stmt = select(ProfessionalProfile).where(
            and_(
                ProfessionalProfile.is_profile_complete.is_(True),
                ProfessionalProfile.availability_status.in_(
                    [AvailabilityStatus.available, AvailabilityStatus.partially_available]
                ),
            )
        )
        result = await self._db.execute(prof_stmt)
        professionals = result.scalars().all()

        scored: list[MatchedProfessional] = []
        for prof in professionals:
            spec_s = _specialization_score(salon_specs, prof.specializations or [])
            loc_s = _location_score(
                salon_city, salon_province,
                prof.preferred_city, prof.preferred_province,
            )
            exp_s = _experience_score(prof.years_of_experience)
            avail_s = _availability_score(prof.availability_status)

            total = 0.40 * spec_s + 0.30 * loc_s + 0.20 * exp_s + 0.10 * avail_s

            scored.append(
                MatchedProfessional(
                    user_id=prof.user_id,
                    first_name=prof.first_name,
                    last_name=prof.last_name,
                    specializations=prof.specializations or [],
                    years_of_experience=prof.years_of_experience,
                    availability_status=prof.availability_status,
                    preferred_city=prof.preferred_city,
                    preferred_province=prof.preferred_province,
                    bio=prof.bio,
                    profile_photo_url=prof.profile_photo_url,
                    is_featured=prof.is_featured,
                    match_score=round(total, 4),
                    score_breakdown=ScoreBreakdown(
                        specialization=round(spec_s, 4),
                        location=round(loc_s, 4),
                        experience=round(exp_s, 4),
                        availability=round(avail_s, 4),
                    ),
                )
            )

        # Sort: featured first within each score tier, then by score desc
        scored.sort(key=lambda m: (m.match_score, m.is_featured), reverse=True)
        return scored[:limit]

    # ── MATCH-003: Recommended jobs for a professional ─────────────────────────

    async def recommended_jobs_for_professional(
        self,
        professional_user_id,
        limit: int = 20,
    ) -> list[MatchedJob]:
        """
        Return up to `limit` open job postings ranked by match score against
        the professional identified by `professional_user_id`.
        """
        # Load professional profile
        prof_stmt = select(ProfessionalProfile).where(
            ProfessionalProfile.user_id == professional_user_id
        )
        prof_result = await self._db.execute(prof_stmt)
        prof = prof_result.scalar_one_or_none()

        if prof is None:
            return []

        prof_specs = prof.specializations or []
        prof_city = prof.preferred_city
        prof_province = prof.preferred_province
        prof_contracts = prof.preferred_contract_types or []

        # Load open job postings
        jobs_stmt = select(JobPosting).where(JobPosting.status == JobStatus.open)
        jobs_result = await self._db.execute(jobs_stmt)
        jobs = jobs_result.scalars().all()

        scored: list[MatchedJob] = []
        for job in jobs:
            spec_s = _specialization_score(prof_specs, job.specializations or [])
            loc_s = _location_score(
                prof_city, prof_province,
                job.city, job.province,
            )
            contract_s = _contract_type_score(prof_contracts, job.contract_types or [])

            total = 0.50 * spec_s + 0.30 * loc_s + 0.20 * contract_s

            scored.append(
                MatchedJob(
                    id=job.id,
                    salon_id=job.salon_id,
                    title=job.title,
                    description=job.description,
                    specializations=job.specializations or [],
                    contract_types=job.contract_types or [],
                    city=job.city,
                    province=job.province,
                    salary_min=float(job.salary_min) if job.salary_min is not None else None,
                    salary_max=float(job.salary_max) if job.salary_max is not None else None,
                    status=job.status,
                    match_score=round(total, 4),
                    score_breakdown=JobScoreBreakdown(
                        specialization=round(spec_s, 4),
                        location=round(loc_s, 4),
                        contract_type=round(contract_s, 4),
                    ),
                )
            )

        scored.sort(key=lambda m: m.match_score, reverse=True)
        return scored[:limit]
