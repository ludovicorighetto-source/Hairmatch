"""
Job service – JOB-001 / JOB-002 / JOB-005 / JOB-006.

Handles job posting CRUD (salon) and application management (professional + salon).
"""

from __future__ import annotations

import logging
import math
import uuid
from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.jobs.schemas import (
    ApplicationResponse,
    ApplicationWithJobResponse,
    CreateApplicationRequest,
    CreateJobPostingRequest,
    JobPostingListResponse,
    JobPostingResponse,
    UpdateApplicationStatusRequest,
    UpdateJobPostingRequest,
)
from app.core.exceptions import DatabaseError, PermissionDeniedError, UserNotFoundError
from app.models.enums import ApplicationStatus, JobStatus, UserRole
from app.models.job_application import JobApplication
from app.models.job_posting import JobPosting
from app.models.user_profile import UserProfile

logger = logging.getLogger(__name__)

PAGE_DEFAULT = 1
LIMIT_DEFAULT = 20


class JobService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _assert_role(self, user_id: uuid.UUID, role: UserRole) -> None:
        result = await self._db.execute(
            select(UserProfile).where(UserProfile.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        if user.role != role:
            raise PermissionDeniedError(f"This action requires {role.value} role")

    async def _get_job(self, job_id: uuid.UUID) -> JobPosting:
        result = await self._db.execute(
            select(JobPosting).where(JobPosting.id == job_id)
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise DatabaseError("Job posting not found")
        return job

    # ── Salon: Create job posting ──────────────────────────────────────────────

    async def create_job_posting(
        self, salon_id: uuid.UUID, payload: CreateJobPostingRequest
    ) -> JobPostingResponse:
        await self._assert_role(salon_id, UserRole.salon)

        job = JobPosting(
            salon_id=salon_id,
            title=payload.title,
            description=payload.description,
            specializations=payload.specializations,
            contract_types=payload.contract_types,
            city=payload.city,
            province=payload.province,
            salary_min=payload.salary_min,
            salary_max=payload.salary_max,
            status=payload.status,
            expires_at=payload.expires_at,
        )
        self._db.add(job)
        await self._db.flush()
        await self._db.refresh(job)
        logger.info("Job posting created: %s by salon %s", job.id, salon_id)
        return JobPostingResponse.model_validate(job)

    # ── Salon: List own job postings ───────────────────────────────────────────

    async def list_salon_jobs(
        self, salon_id: uuid.UUID, page: int = PAGE_DEFAULT, limit: int = LIMIT_DEFAULT
    ) -> JobPostingListResponse:
        await self._assert_role(salon_id, UserRole.salon)

        count_stmt = select(JobPosting).where(JobPosting.salon_id == salon_id)
        all_result = await self._db.execute(count_stmt)
        all_jobs = all_result.scalars().all()
        total = len(all_jobs)

        offset = (page - 1) * limit
        page_result = await self._db.execute(
            select(JobPosting)
            .where(JobPosting.salon_id == salon_id)
            .order_by(JobPosting.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        jobs = page_result.scalars().all()

        return JobPostingListResponse(
            items=[JobPostingResponse.model_validate(j) for j in jobs],
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if total else 1,
        )

    # ── Salon: Update job posting ──────────────────────────────────────────────

    async def update_job_posting(
        self, salon_id: uuid.UUID, job_id: uuid.UUID, payload: UpdateJobPostingRequest
    ) -> JobPostingResponse:
        await self._assert_role(salon_id, UserRole.salon)
        job = await self._get_job(job_id)

        if job.salon_id != salon_id:
            raise PermissionDeniedError("You can only edit your own job postings")

        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(job, field, value)

        await self._db.flush()
        await self._db.refresh(job)
        return JobPostingResponse.model_validate(job)

    # ── Salon: Delete job posting ──────────────────────────────────────────────

    async def delete_job_posting(self, salon_id: uuid.UUID, job_id: uuid.UUID) -> None:
        await self._assert_role(salon_id, UserRole.salon)
        job = await self._get_job(job_id)

        if job.salon_id != salon_id:
            raise PermissionDeniedError("You can only delete your own job postings")

        await self._db.delete(job)
        await self._db.flush()
        logger.info("Job posting deleted: %s by salon %s", job_id, salon_id)

    # ── Salon: View applicants for a job ──────────────────────────────────────

    async def list_applicants(
        self, salon_id: uuid.UUID, job_id: uuid.UUID
    ) -> List[ApplicationResponse]:
        await self._assert_role(salon_id, UserRole.salon)
        job = await self._get_job(job_id)

        if job.salon_id != salon_id:
            raise PermissionDeniedError("You can only view applicants for your own job postings")

        result = await self._db.execute(
            select(JobApplication)
            .where(JobApplication.job_id == job_id)
            .order_by(JobApplication.created_at.desc())
        )
        apps = result.scalars().all()
        return [ApplicationResponse.model_validate(a) for a in apps]

    # ── Salon: Update application status ──────────────────────────────────────

    async def update_application_status(
        self,
        salon_id: uuid.UUID,
        application_id: uuid.UUID,
        payload: UpdateApplicationStatusRequest,
    ) -> ApplicationResponse:
        await self._assert_role(salon_id, UserRole.salon)

        result = await self._db.execute(
            select(JobApplication)
            .where(JobApplication.id == application_id)
            .options(selectinload(JobApplication.job))
        )
        app = result.scalar_one_or_none()
        if app is None:
            raise DatabaseError("Application not found")

        if app.job.salon_id != salon_id:
            raise PermissionDeniedError("You can only manage applications for your own postings")

        app.status = payload.status
        await self._db.flush()
        await self._db.refresh(app)
        return ApplicationResponse.model_validate(app)

    # ── Public: Browse open job postings ──────────────────────────────────────

    async def browse_jobs(
        self,
        city: str | None = None,
        province: str | None = None,
        specializations: List[str] | None = None,
        page: int = PAGE_DEFAULT,
        limit: int = LIMIT_DEFAULT,
    ) -> JobPostingListResponse:
        filters = [JobPosting.status == JobStatus.open]

        if city:
            from sqlalchemy import func  # noqa: PLC0415
            filters.append(func.lower(JobPosting.city) == city.lower())

        if province:
            from sqlalchemy import func  # noqa: PLC0415
            filters.append(func.lower(JobPosting.province) == province.lower())

        from sqlalchemy import and_  # noqa: PLC0415

        all_result = await self._db.execute(select(JobPosting).where(and_(*filters)))
        all_jobs = list(all_result.scalars().all())

        # Specialization filter in Python (DB-agnostic)
        if specializations:
            requested = {s.lower() for s in specializations}
            all_jobs = [
                j for j in all_jobs
                if any(spec.lower() in requested for spec in (j.specializations or []))
            ]

        total = len(all_jobs)
        offset = (page - 1) * limit
        page_items = all_jobs[offset: offset + limit]

        return JobPostingListResponse(
            items=[JobPostingResponse.model_validate(j) for j in page_items],
            total=total,
            page=page,
            limit=limit,
            pages=math.ceil(total / limit) if total else 1,
        )

    # ── Professional: Apply to a job ──────────────────────────────────────────

    async def apply_to_job(
        self,
        professional_id: uuid.UUID,
        job_id: uuid.UUID,
        payload: CreateApplicationRequest,
    ) -> ApplicationResponse:
        await self._assert_role(professional_id, UserRole.professional)
        job = await self._get_job(job_id)

        if job.status != JobStatus.open:
            raise PermissionDeniedError("This job posting is not accepting applications")

        # Check for duplicate application
        existing = await self._db.execute(
            select(JobApplication).where(
                and_(
                    JobApplication.job_id == job_id,
                    JobApplication.professional_id == professional_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise DatabaseError("You have already applied to this job")

        app = JobApplication(
            job_id=job_id,
            professional_id=professional_id,
            cover_letter=payload.cover_letter,
            status=ApplicationStatus.pending,
        )
        self._db.add(app)
        await self._db.flush()
        await self._db.refresh(app)
        logger.info("Professional %s applied to job %s", professional_id, job_id)
        return ApplicationResponse.model_validate(app)

    # ── Professional: My applications ─────────────────────────────────────────

    async def my_applications(
        self, professional_id: uuid.UUID
    ) -> List[ApplicationWithJobResponse]:
        await self._assert_role(professional_id, UserRole.professional)

        result = await self._db.execute(
            select(JobApplication)
            .where(JobApplication.professional_id == professional_id)
            .options(selectinload(JobApplication.job))
            .order_by(JobApplication.created_at.desc())
        )
        apps = result.scalars().all()
        return [
            ApplicationWithJobResponse(
                id=a.id,
                job_id=a.job_id,
                professional_id=a.professional_id,
                cover_letter=a.cover_letter,
                status=a.status,
                created_at=a.created_at,
                updated_at=a.updated_at,
                job=JobPostingResponse.model_validate(a.job),
            )
            for a in apps
        ]

    # ── Professional: Withdraw application ────────────────────────────────────

    async def withdraw_application(
        self, professional_id: uuid.UUID, application_id: uuid.UUID
    ) -> ApplicationResponse:
        await self._assert_role(professional_id, UserRole.professional)

        result = await self._db.execute(
            select(JobApplication).where(JobApplication.id == application_id)
        )
        app = result.scalar_one_or_none()
        if app is None:
            raise DatabaseError("Application not found")
        if app.professional_id != professional_id:
            raise PermissionDeniedError("You can only withdraw your own applications")
        if app.status == ApplicationStatus.withdrawn:
            raise PermissionDeniedError("Application already withdrawn")

        app.status = ApplicationStatus.withdrawn
        await self._db.flush()
        await self._db.refresh(app)
        return ApplicationResponse.model_validate(app)
