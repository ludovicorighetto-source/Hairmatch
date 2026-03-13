from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Always stored with participant_a_id < participant_b_id (by UUID str)
    participant_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    participant_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "participant_a_id", "participant_b_id",
            name="uq_conversation_participants"
        ),
    )

    messages: Mapped[List["Message"]] = relationship(  # noqa: F821
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} a={self.participant_a_id} b={self.participant_b_id}>"
