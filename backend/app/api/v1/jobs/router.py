"""
Jobs router – JOB-001 through JOB-007.

Salon endpoints (require salon JWT):
  POST   /api/v1/jobs/                              → create job posting
  GET    /api/v1/jobs/mine                          → list own postings
  PATCH  /api/v1/jobs/{job_id}                      → update posting
  DELETE /api/v1/jobs/{job_id}                      → delete posting
  GET    /api/v1/jobs/{job_id}/applications         → list applicants
  PATCH  /api/v1/jobs/applications/{app_id}/status  → accept/reject application

Professional endpoints (require professional JWT):
  GET    /api/v1/jobs/                              → browse open jobs (public, no auth)
  POST   /api/v1/jobs/{job_id}/apply               → apply
  GET    /api/v1/jobs/applications/mine             → my applications
  PATCH  /api/v1/jobs/applications/{app_id}/withdraw → withdraw
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.api.v1.jobs.service import JobService
from app.dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_service(db: AsyncSession = Depends(get_db)) -> JobService:
    return JobService(db=db)


# ── Public: Browse open jobs ───────────────────────────────────────────────────

@router.get(
    "",
    response_model=JobPostingListResponse,
    status_code=status.HTTP_200_OK,
    summary="Browse open job postings (public)",
)
async def browse_jobs(
    city: Optional[str] = Query(default=None, max_length=100),
    province: Optional[str] = Query(default=None, max_length=5),
    specializations: Optional[List[str]] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: JobService = Depends(_get_service),
) -> JobPostingListResponse:
    return await service.browse_jobs(
        city=city,
        province=province,
        specializations=specializations,
        page=page,
        limit=limit,
    )


# ── Salon: Create job posting ──────────────────────────────────────────────────

@router.post(
    "",
    response_model=JobPostingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job posting (salon only)",
)
async def create_job_posting(
    payload: CreateJobPostingRequest,
    salon_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> JobPostingResponse:
    return await service.create_job_posting(salon_id, payload)


# ── Salon: List own job postings ───────────────────────────────────────────────

@router.get(
    "/mine",
    response_model=JobPostingListResponse,
    status_code=status.HTTP_200_OK,
    summary="List own job postings (salon only)",
)
async def list_my_jobs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    salon_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> JobPostingListResponse:
    return await service.list_salon_jobs(salon_id, page=page, limit=limit)


# ── Professional: My applications ─────────────────────────────────────────────

@router.get(
    "/applications/mine",
    response_model=List[ApplicationWithJobResponse],
    status_code=status.HTTP_200_OK,
    summary="Get my applications (professional only)",
)
async def my_applications(
    professional_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> List[ApplicationWithJobResponse]:
    return await service.my_applications(professional_id)


# ── Salon: Update job posting ──────────────────────────────────────────────────

@router.patch(
    "/{job_id}",
    response_model=JobPostingResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a job posting (salon only)",
)
async def update_job_posting(
    job_id: uuid.UUID,
    payload: UpdateJobPostingRequest,
    salon_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> JobPostingResponse:
    return await service.update_job_posting(salon_id, job_id, payload)


# ── Salon: Delete job posting ──────────────────────────────────────────────────

@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job posting (salon only)",
)
async def delete_job_posting(
    job_id: uuid.UUID,
    salon_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> None:
    await service.delete_job_posting(salon_id, job_id)


# ── Salon: View applicants ─────────────────────────────────────────────────────

@router.get(
    "/{job_id}/applications",
    response_model=List[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="List applicants for a job posting (salon only)",
)
async def list_applicants(
    job_id: uuid.UUID,
    salon_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> List[ApplicationResponse]:
    return await service.list_applicants(salon_id, job_id)


# ── Professional: Apply to a job ───────────────────────────────────────────────

@router.post(
    "/{job_id}/apply",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply to a job posting (professional only)",
)
async def apply_to_job(
    job_id: uuid.UUID,
    payload: CreateApplicationRequest,
    professional_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> ApplicationResponse:
    return await service.apply_to_job(professional_id, job_id, payload)


# ── Salon: Update application status ──────────────────────────────────────────

@router.patch(
    "/applications/{app_id}/status",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept or reject an application (salon only)",
)
async def update_application_status(
    app_id: uuid.UUID,
    payload: UpdateApplicationStatusRequest,
    salon_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> ApplicationResponse:
    return await service.update_application_status(salon_id, app_id, payload)


# ── Professional: Withdraw application ────────────────────────────────────────

@router.patch(
    "/applications/{app_id}/withdraw",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw an application (professional only)",
)
async def withdraw_application(
    app_id: uuid.UUID,
    professional_id: uuid.UUID = Depends(get_current_user_id),
    service: JobService = Depends(_get_service),
) -> ApplicationResponse:
    return await service.withdraw_application(professional_id, app_id)
