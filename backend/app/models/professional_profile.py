import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AvailabilityStatus, SubscriptionPlan, availability_status_enum, subscription_plan_enum


class ProfessionalProfile(Base):
    __tablename__ = "professional_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Personal information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Professional details
    specializations: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )
    years_of_experience: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Work preferences
    preferred_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_province: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    max_travel_km: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    is_available_remotely: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    preferred_contract_types: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )

    # Availability
    availability_status: Mapped[AvailabilityStatus] = mapped_column(
        availability_status_enum,
        nullable=False,
        default=AvailabilityStatus.available,
        server_default="available",
    )

    # Media
    profile_photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio_urls: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )

    # Subscription
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        subscription_plan_enum,
        nullable=False,
        default=SubscriptionPlan.free,
        server_default="free",
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Profile status
    is_profile_complete: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    user: Mapped["UserProfile"] = relationship(  # noqa: F821
        "UserProfile",
        back_populates="professional_profile",
    )

    def __repr__(self) -> str:
        return f"<ProfessionalProfile id={self.id} name={self.first_name} {self.last_name}>"
