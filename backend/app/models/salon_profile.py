import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import SubscriptionPlan, subscription_plan_enum


class SalonProfile(Base):
    __tablename__ = "salon_profiles"

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

    # Business information
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vat_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Address
    address_street: Mapped[str] = mapped_column(String(255), nullable=False)
    address_city: Mapped[str] = mapped_column(String(100), nullable=False)
    address_province: Mapped[str] = mapped_column(String(5), nullable=False)
    address_postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    address_country: Mapped[str] = mapped_column(String(2), default="IT", server_default="IT", nullable=False)

    # Geolocation
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)

    # Salon details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seats_count: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    opening_hours: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)

    # Media
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Subscription
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        subscription_plan_enum,
        default=SubscriptionPlan.free,
        server_default="free",
        nullable=False,
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Profile status
    is_profile_complete: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
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
        back_populates="salon_profile",
    )

    def __repr__(self) -> str:
        return f"<SalonProfile id={self.id} business_name={self.business_name}>"
