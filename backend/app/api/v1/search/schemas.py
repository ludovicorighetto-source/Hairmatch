"""
Pydantic schemas for SEARCH-001 / SEARCH-002.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.models.enums import AvailabilityStatus, SubscriptionPlan


# ─────────────────────────────────────────────────────────────────────────────
# Query params
# ─────────────────────────────────────────────────────────────────────────────


class SearchProfessionalsQuery(BaseModel):
    """Query parameters for professional search."""

    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=5)
    specializations: Optional[List[str]] = Field(default=None)
    availability_status: Optional[AvailabilityStatus] = None
    # Geolocation radius filter (requires lat/lon of the searcher)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    max_km: Optional[float] = Field(default=None, ge=0, le=500)
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class SearchSalonsQuery(BaseModel):
    """Query parameters for salon search."""

    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=5)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    max_km: Optional[float] = Field(default=None, ge=0, le=500)
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


# ─────────────────────────────────────────────────────────────────────────────
# Result cards (trimmed public view)
# ─────────────────────────────────────────────────────────────────────────────


class ProfessionalCard(BaseModel):
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
    is_profile_complete: bool
    subscription_plan: SubscriptionPlan
    distance_km: Optional[float] = None

    model_config = {"from_attributes": True}


class SalonCard(BaseModel):
    user_id: uuid.UUID
    business_name: str
    address_city: str
    address_province: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    seats_count: Optional[int] = None
    is_featured: bool
    is_profile_complete: bool
    subscription_plan: SubscriptionPlan
    distance_km: Optional[float] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Paginated responses
# ─────────────────────────────────────────────────────────────────────────────


class PaginatedProfessionals(BaseModel):
    items: List[ProfessionalCard]
    total: int
    page: int
    limit: int
    pages: int


class PaginatedSalons(BaseModel):
    items: List[SalonCard]
    total: int
    page: int
    limit: int
    pages: int
