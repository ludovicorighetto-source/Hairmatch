"""
Pydantic schemas for PROFILE-001 / PROFILE-002 endpoints.

All update schemas use Optional fields (partial update / PATCH semantics).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.enums import AvailabilityStatus, SubscriptionPlan, UserRole


# ─────────────────────────────────────────────────────────────────────────────
# Shared
# ─────────────────────────────────────────────────────────────────────────────


class OpeningHoursDay(BaseModel):
    """Represents opening hours for a single weekday."""

    open: str = Field(..., description="Opening time, e.g. '09:00'")
    close: str = Field(..., description="Closing time, e.g. '19:00'")
    closed: bool = Field(default=False)


OpeningHoursSchema = Dict[str, Optional[OpeningHoursDay]]
"""Keys are weekday names: monday…sunday. None = closed."""


# ─────────────────────────────────────────────────────────────────────────────
# Salon Profile – PATCH (PROFILE-001)
# ─────────────────────────────────────────────────────────────────────────────


class UpdateSalonProfileRequest(BaseModel):
    """Partial update – only provided fields are written."""

    business_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=6, max_length=30)
    description: Optional[str] = Field(default=None, max_length=2000)
    website_url: Optional[str] = Field(default=None, max_length=500)
    vat_number: Optional[str] = Field(default=None, max_length=20)

    # Address
    address_street: Optional[str] = Field(default=None, max_length=255)
    address_city: Optional[str] = Field(default=None, max_length=100)
    address_province: Optional[str] = Field(default=None, min_length=2, max_length=5)
    address_postal_code: Optional[str] = Field(default=None, min_length=4, max_length=10)

    # Business details
    seats_count: Optional[int] = Field(default=None, ge=1, le=500)
    opening_hours: Optional[OpeningHoursSchema] = None

    # Geolocation
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    # Media URLs (set by upload endpoint, but can be updated directly)
    logo_url: Optional[str] = Field(default=None, max_length=1000)
    cover_image_url: Optional[str] = Field(default=None, max_length=1000)


class SalonProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    business_name: str
    phone: str
    address_street: str
    address_city: str
    address_province: str
    address_postal_code: str
    address_country: str
    vat_number: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    seats_count: Optional[int] = None
    opening_hours: Optional[Any] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    subscription_plan: SubscriptionPlan
    subscription_expires_at: Optional[datetime] = None
    is_profile_complete: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Professional Profile – PATCH (PROFILE-002)
# ─────────────────────────────────────────────────────────────────────────────


class UpdateProfessionalProfileRequest(BaseModel):
    """Partial update – only provided fields are written."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=6, max_length=30)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(default=None, max_length=2000)

    specializations: Optional[List[str]] = None
    years_of_experience: Optional[int] = Field(default=None, ge=0, le=80)

    # Work preferences
    preferred_city: Optional[str] = Field(default=None, max_length=100)
    preferred_province: Optional[str] = Field(default=None, max_length=5)
    max_travel_km: Optional[int] = Field(default=None, ge=0, le=1000)
    is_available_remotely: Optional[bool] = None
    preferred_contract_types: Optional[List[str]] = None

    # Availability
    availability_status: Optional[AvailabilityStatus] = None

    # Media
    profile_photo_url: Optional[str] = Field(default=None, max_length=1000)
    portfolio_urls: Optional[List[str]] = None


class ProfessionalProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    phone: str
    date_of_birth: Optional[date] = None
    bio: Optional[str] = None
    specializations: List[str]
    years_of_experience: Optional[int] = None
    preferred_city: Optional[str] = None
    preferred_province: Optional[str] = None
    max_travel_km: int
    is_available_remotely: bool
    preferred_contract_types: List[str]
    availability_status: AvailabilityStatus
    profile_photo_url: Optional[str] = None
    portfolio_urls: List[str]
    subscription_plan: SubscriptionPlan
    subscription_expires_at: Optional[datetime] = None
    is_profile_complete: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Public profile response (GET /profiles/{user_id})
# ─────────────────────────────────────────────────────────────────────────────


class PublicUserResponse(BaseModel):
    id: uuid.UUID
    role: UserRole
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicSalonProfileResponse(BaseModel):
    user: PublicUserResponse
    profile: SalonProfileResponse


class PublicProfessionalProfileResponse(BaseModel):
    user: PublicUserResponse
    profile: ProfessionalProfileResponse
