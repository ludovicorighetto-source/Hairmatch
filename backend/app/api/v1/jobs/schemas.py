"""
Pydantic schemas for JOB-001 / JOB-002 / JOB-005 / JOB-006.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.enums import ApplicationStatus, JobStatus


# ─────────────────────────────────────────────────────────────────────────────
# Job Posting
# ─────────────────────────────────────────────────────────────────────────────


class CreateJobPostingRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10, max_length=5000)
    specializations: List[str] = Field(default_factory=list)
    contract_types: List[str] = Field(default_factory=list)
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=5)
    salary_min: Optional[Decimal] = Field(default=None, ge=0)
    salary_max: Optional[Decimal] = Field(default=None, ge=0)
    status: JobStatus = Field(default=JobStatus.open)
    expires_at: Optional[datetime] = None


class UpdateJobPostingRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10, max_length=5000)
    specializations: Optional[List[str]] = None
    contract_types: Optional[List[str]] = None
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=5)
    salary_min: Optional[Decimal] = Field(default=None, ge=0)
    salary_max: Optional[Decimal] = Field(default=None, ge=0)
    status: Optional[JobStatus] = None
    expires_at: Optional[datetime] = None


class JobPostingResponse(BaseModel):
    id: uuid.UUID
    salon_id: uuid.UUID
    title: str
    description: str
    specializations: List[str]
    contract_types: List[str]
    city: Optional[str] = None
    province: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    status: JobStatus
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobPostingListResponse(BaseModel):
    items: List[JobPostingResponse]
    total: int
    page: int
    limit: int
    pages: int


# ─────────────────────────────────────────────────────────────────────────────
# Applications
# ─────────────────────────────────────────────────────────────────────────────


class CreateApplicationRequest(BaseModel):
    cover_letter: Optional[str] = Field(default=None, max_length=3000)


class UpdateApplicationStatusRequest(BaseModel):
    """Salon uses this to accept/reject. Professional uses withdrawn."""

    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    professional_id: uuid.UUID
    cover_letter: Optional[str] = None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationWithJobResponse(BaseModel):
    """Used in professional's "my applications" list."""

    id: uuid.UUID
    job_id: uuid.UUID
    professional_id: uuid.UUID
    cover_letter: Optional[str] = None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    job: JobPostingResponse

    model_config = {"from_attributes": True}
