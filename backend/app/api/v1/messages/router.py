"""
Messages router – MSG-002.

POST   /api/v1/messages/conversations              → start or fetch conversation
GET    /api/v1/messages/conversations              → list user's conversations
GET    /api/v1/messages/conversations/{id}/messages → paginated messages
POST   /api/v1/messages/conversations/{id}/messages → send message
PATCH  /api/v1/messages/conversations/{id}/read    → mark as read
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.messages.schemas import (
    ConversationResponse,
    MessageResponse,
    SendMessageRequest,
    StartConversationRequest,
)
from app.api.v1.messages.service import MessagingService
from app.dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/messages", tags=["messages"])


def _get_service(db: AsyncSession = Depends(get_db)) -> MessagingService:
    return MessagingService(db)


# ── Start / get conversation ──────────────────────────────────────────────────

@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start or retrieve a 1-to-1 conversation",
)
async def start_conversation(
    payload: StartConversationRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    service: MessagingService = Depends(_get_service),
) -> ConversationResponse:
    return await service.get_or_create_conversation(
        current_user_id=current_user_id,
        other_user_id=payload.other_user_id,
        initial_message=payload.initial_message,
    )


# ── List conversations (inbox) ────────────────────────────────────────────────

@router.get(
    "/conversations",
    response_model=List[ConversationResponse],
    summary="List all conversations for the current user",
)
async def list_conversations(
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    service: MessagingService = Depends(_get_service),
) -> List[ConversationResponse]:
    return await service.list_conversations(current_user_id)


# ── Get messages ──────────────────────────────────────────────────────────────

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Get paginated messages in a conversation",
)
async def get_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    before_id: Optional[uuid.UUID] = Query(default=None),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    service: MessagingService = Depends(_get_service),
) -> List[MessageResponse]:
    return await service.get_messages(
        current_user_id=current_user_id,
        conversation_id=conversation_id,
        limit=limit,
        before_id=before_id,
    )


# ── Send message ──────────────────────────────────────────────────────────────

@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in a conversation",
)
async def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    service: MessagingService = Depends(_get_service),
) -> MessageResponse:
    return await service.send_message(
        current_user_id=current_user_id,
        conversation_id=conversation_id,
        content=payload.content,
    )


# ── Mark as read ──────────────────────────────────────────────────────────────

@router.patch(
    "/conversations/{conversation_id}/read",
    summary="Mark all messages in conversation as read",
)
async def mark_as_read(
    conversation_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    service: MessagingService = Depends(_get_service),
) -> dict:
    count = await service.mark_as_read(
        current_user_id=current_user_id,
        conversation_id=conversation_id,
    )
    return {"marked_read": count}
