"""Pydantic schemas for MSG-001 / MSG-002."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: uuid.UUID
    participant_a_id: uuid.UUID
    participant_b_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Enriched fields
    other_user_id: uuid.UUID
    unread_count: int
    last_message: Optional[MessageResponse] = None

    model_config = {"from_attributes": True}


class StartConversationRequest(BaseModel):
    other_user_id: uuid.UUID
    initial_message: Optional[str] = Field(default=None, max_length=5000)
