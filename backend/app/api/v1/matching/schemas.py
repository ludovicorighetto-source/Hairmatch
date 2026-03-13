"""Pydantic schemas for MATCH-001/002/003."""

from __future__ import annotations

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.enums import AvailabilityStatus, JobStatus


class MatchedProfessional(BaseModel):
    """Professional card enriched with a match score for a salon."""

    user_id: uuid.UUID
    first_name: str
    last_name: str
    specializations: List[str]
    years_of_experience: Optional[int] = None
    availability_status: AvailabilityStatus
    preferred_city: Optional[str] = None
    preferred_province: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    is_featured: bool

    # Matching
    match_score: float = Field(..., ge=0.0, le=1.0, description="0–1 composite score")
    score_breakdown: "ScoreBreakdown"

    model_config = {"from_attributes": True}


class ScoreBreakdown(BaseModel):
    specialization: float = Field(..., ge=0.0, le=1.0)
    location: float = Field(..., ge=0.0, le=1.0)
    experience: float = Field(..., ge=0.0, le=1.0)
    availability: float = Field(..., ge=0.0, le=1.0)


MatchedProfessional.model_rebuild()


class MatchedJob(BaseModel):
    """Job posting enriched with a match score for a professional."""

    id: uuid.UUID
    salon_id: uuid.UUID
    title: str
    description: str
    specializations: List[str]
    contract_types: List[str]
    city: Optional[str] = None
    province: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: JobStatus

    # Matching
    match_score: float = Field(..., ge=0.0, le=1.0)
    score_breakdown: "JobScoreBreakdown"

    model_config = {"from_attributes": True}


class JobScoreBreakdown(BaseModel):
    specialization: float = Field(..., ge=0.0, le=1.0)
    location: float = Field(..., ge=0.0, le=1.0)
    contract_type: float = Field(..., ge=0.0, le=1.0)


MatchedJob.model_rebuild()
