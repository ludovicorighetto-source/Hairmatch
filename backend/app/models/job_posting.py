from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import JobStatus, job_status_enum


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    salon_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    specializations: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )
    contract_types: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )

    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    province: Mapped[Optional[str]] = mapped_column(String(5), nullable=True, index=True)

    salary_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    salary_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    status: Mapped[JobStatus] = mapped_column(
        job_status_enum, nullable=False, server_default="open", index=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    applications: Mapped[List["JobApplication"]] = relationship(  # noqa: F821
        "JobApplication", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JobPosting id={self.id} title={self.title!r} status={self.status}>"
