"""
Pydantic v2 schemas for AUTH-001 endpoints.

Naming convention:
  - *Request  → inbound payload validated by FastAPI
  - *Response → outbound payload returned to the client
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.security import validate_password_strength
from app.models.enums import AvailabilityStatus, SubscriptionPlan, UserRole


# ─────────────────────────────────────────────────────────────────────────────
# Shared / base schemas
# ─────────────────────────────────────────────────────────────────────────────


class AddressSchema(BaseModel):
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    province: str = Field(..., min_length=2, max_length=5)
    postal_code: str = Field(..., min_length=4, max_length=10)
    country: str = Field(default="IT", min_length=2, max_length=2)


# ─────────────────────────────────────────────────────────────────────────────
# Register Salon
# ─────────────────────────────────────────────────────────────────────────────


class RegisterSalonRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    business_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=6, max_length=30)
    address: AddressSchema
    vat_number: Optional[str] = Field(default=None, max_length=20)
    website_url: Optional[str] = Field(default=None, max_length=500)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v


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
# Register Professional
# ─────────────────────────────────────────────────────────────────────────────


class RegisterProfessionalRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=6, max_length=30)
    date_of_birth: Optional[date] = None
    specializations: List[str] = Field(default_factory=list)
    years_of_experience: Optional[int] = Field(default=None, ge=0, le=80)
    preferred_city: Optional[str] = Field(default=None, max_length=100)
    preferred_province: Optional[str] = Field(default=None, max_length=5)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v


class ProfessionalProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    phone: str
    date_of_birth: Optional[date] = None
    specializations: List[str]
    years_of_experience: Optional[int] = None
    bio: Optional[str] = None
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
# User profile in responses
# ─────────────────────────────────────────────────────────────────────────────


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Register responses
# ─────────────────────────────────────────────────────────────────────────────


class RegisterSalonResponse(BaseModel):
    user: UserProfileResponse
    profile: SalonProfileResponse
    message: str = "Salon registered successfully. Please verify your email."


class RegisterProfessionalResponse(BaseModel):
    user: UserProfileResponse
    profile: ProfessionalProfileResponse
    message: str = "Professional registered successfully. Please verify your email."


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifetime in seconds")


class LoginSalonResponse(BaseModel):
    tokens: TokenPair
    user: UserProfileResponse
    profile: SalonProfileResponse


class LoginProfessionalResponse(BaseModel):
    tokens: TokenPair
    user: UserProfileResponse
    profile: ProfessionalProfileResponse


class LoginResponse(BaseModel):
    """Generic login response that includes either a salon or professional profile."""

    tokens: TokenPair
    user: UserProfileResponse
    profile: SalonProfileResponse | ProfessionalProfileResponse


# ─────────────────────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────────────────────


class LogoutRequest(BaseModel):
    """Optional body – client may send the refresh_token to invalidate it in Redis."""

    refresh_token: Optional[str] = None


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"


# ─────────────────────────────────────────────────────────────────────────────
# Refresh
# ─────────────────────────────────────────────────────────────────────────────


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RefreshResponse(BaseModel):
    tokens: TokenPair


# ─────────────────────────────────────────────────────────────────────────────
# Me (current user)
# ─────────────────────────────────────────────────────────────────────────────


class MeSalonResponse(BaseModel):
    user: UserProfileResponse
    profile: SalonProfileResponse


class MeProfessionalResponse(BaseModel):
    user: UserProfileResponse
    profile: ProfessionalProfileResponse


class MeResponse(BaseModel):
    user: UserProfileResponse
    profile: SalonProfileResponse | ProfessionalProfileResponse


# ─────────────────────────────────────────────────────────────────────────────
# Resend Verification (AUTH-002)
# ─────────────────────────────────────────────────────────────────────────────


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    message: str = (
        "Se l'email è registrata e non ancora verificata, riceverai un nuovo link a breve."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Password Reset (AUTH-003)
# ─────────────────────────────────────────────────────────────────────────────


class RequestPasswordResetRequest(BaseModel):
    email: EmailStr


class RequestPasswordResetResponse(BaseModel):
    message: str = "Se l'email è registrata, riceverai le istruzioni per reimpostare la password."


class ResetPasswordRequest(BaseModel):
    access_token: str = Field(..., description="Token ricevuto via email da Supabase")
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v


class ResetPasswordResponse(BaseModel):
    message: str = "Password reimpostata con successo."
