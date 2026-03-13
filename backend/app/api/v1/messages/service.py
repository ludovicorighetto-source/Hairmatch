"""
Messaging service – MSG-002.

Business rules:
- Conversations are 1-to-1 between any two users.
- participant_a_id < participant_b_id (by UUID string) to ensure uniqueness.
- Only conversation participants can read/send messages.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.messages.schemas import ConversationResponse, MessageResponse
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.conversation import Conversation
from app.models.message import Message


def _ordered_participants(a: uuid.UUID, b: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    """Return (min, max) to ensure canonical participant ordering."""
    return (a, b) if str(a) < str(b) else (b, a)


class MessagingService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Get or create conversation ─────────────────────────────────────────────

    async def get_or_create_conversation(
        self,
        current_user_id: uuid.UUID,
        other_user_id: uuid.UUID,
        initial_message: str | None = None,
    ) -> ConversationResponse:
        p_a, p_b = _ordered_participants(current_user_id, other_user_id)

        # Check if exists
        stmt = select(Conversation).where(
            and_(
                Conversation.participant_a_id == p_a,
                Conversation.participant_b_id == p_b,
            )
        )
        result = await self._db.execute(stmt)
        conv = result.scalar_one_or_none()

        if conv is None:
            conv = Conversation(participant_a_id=p_a, participant_b_id=p_b)
            self._db.add(conv)
            await self._db.flush()
            await self._db.refresh(conv)

        if initial_message:
            msg = Message(
                conversation_id=conv.id,
                sender_id=current_user_id,
                content=initial_message,
            )
            self._db.add(msg)
            await self._db.flush()

        return await self._build_conversation_response(conv, current_user_id)

    # ── List conversations ─────────────────────────────────────────────────────

    async def list_conversations(
        self, current_user_id: uuid.UUID
    ) -> List[ConversationResponse]:
        stmt = (
            select(Conversation)
            .where(
                or_(
                    Conversation.participant_a_id == current_user_id,
                    Conversation.participant_b_id == current_user_id,
                )
            )
            .order_by(Conversation.updated_at.desc())
        )
        result = await self._db.execute(stmt)
        convs = result.scalars().all()

        responses = []
        for conv in convs:
            responses.append(
                await self._build_conversation_response(conv, current_user_id)
            )
        return responses

    # ── Get messages in conversation ───────────────────────────────────────────

    async def get_messages(
        self,
        current_user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        limit: int = 50,
        before_id: uuid.UUID | None = None,
    ) -> List[MessageResponse]:
        conv = await self._get_conversation_or_403(conversation_id, current_user_id)

        filters = [Message.conversation_id == conv.id]
        if before_id:
            # Cursor-based pagination (older messages)
            cursor_stmt = select(Message.created_at).where(Message.id == before_id)
            cursor_result = await self._db.execute(cursor_stmt)
            cursor_ts = cursor_result.scalar_one_or_none()
            if cursor_ts:
                filters.append(Message.created_at < cursor_ts)

        stmt = (
            select(Message)
            .where(and_(*filters))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        messages = result.scalars().all()
        # Return in chronological order
        messages = list(reversed(messages))
        return [MessageResponse.model_validate(m) for m in messages]

    # ── Send message ───────────────────────────────────────────────────────────

    async def send_message(
        self,
        current_user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        content: str,
    ) -> MessageResponse:
        conv = await self._get_conversation_or_403(conversation_id, current_user_id)

        msg = Message(
            conversation_id=conv.id,
            sender_id=current_user_id,
            content=content,
        )
        self._db.add(msg)
        # Update conversation.updated_at so it bubbles up in inbox sort
        conv.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
        await self._db.flush()
        await self._db.refresh(msg)
        return MessageResponse.model_validate(msg)

    # ── Mark as read ───────────────────────────────────────────────────────────

    async def mark_as_read(
        self,
        current_user_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ) -> int:
        conv = await self._get_conversation_or_403(conversation_id, current_user_id)

        # Mark all unread messages NOT sent by current user
        stmt = (
            select(Message)
            .where(
                and_(
                    Message.conversation_id == conv.id,
                    Message.sender_id != current_user_id,
                    Message.is_read.is_(False),
                )
            )
        )
        result = await self._db.execute(stmt)
        unread = result.scalars().all()
        for m in unread:
            m.is_read = True
        await self._db.flush()
        return len(unread)

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _get_conversation_or_403(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Conversation:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self._db.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv is None:
            raise NotFoundError("Conversation not found")
        if user_id not in (conv.participant_a_id, conv.participant_b_id):
            raise PermissionDeniedError("Not a participant in this conversation")
        return conv

    async def _build_conversation_response(
        self, conv: Conversation, current_user_id: uuid.UUID
    ) -> ConversationResponse:
        other_user_id = (
            conv.participant_b_id
            if conv.participant_a_id == current_user_id
            else conv.participant_a_id
        )

        # Unread count
        unread_stmt = select(func.count()).where(
            and_(
                Message.conversation_id == conv.id,
                Message.sender_id != current_user_id,
                Message.is_read.is_(False),
            )
        )
        unread_result = await self._db.execute(unread_stmt)
        unread_count = unread_result.scalar_one()

        # Last message
        last_stmt = (
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_result = await self._db.execute(last_stmt)
        last_msg_row = last_result.scalar_one_or_none()
        last_message = MessageResponse.model_validate(last_msg_row) if last_msg_row else None

        return ConversationResponse(
            id=conv.id,
            participant_a_id=conv.participant_a_id,
            participant_b_id=conv.participant_b_id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            other_user_id=other_user_id,
            unread_count=unread_count,
            last_message=last_message,
        )
