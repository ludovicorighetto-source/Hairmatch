"""
FastAPI dependency injectors.

Provides:
  - get_db        → async SQLAlchemy session
  - get_redis     → async Redis client
  - get_raw_token → extracts the raw Bearer token string from Authorization header
  - get_current_user_id → verifies JWT and returns user UUID
"""

from __future__ import annotations

import uuid
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import extract_user_id_from_token
from app.database import AsyncSessionFactory

settings = get_settings()

# ── Database ───────────────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session, commit on success, rollback on error."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Redis ──────────────────────────────────────────────────────────────────────

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """
    Return a module-level Redis connection pool.

    The pool is created lazily on first use so that the application can start
    even if Redis is temporarily unavailable.
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
    return _redis_pool


# ── Bearer token extraction ────────────────────────────────────────────────────

_bearer_scheme = HTTPBearer(auto_error=True)


async def get_raw_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """
    Extract and return the raw JWT string from the ``Authorization: Bearer <token>`` header.

    Raises HTTP 401 if the header is absent or malformed.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Missing authentication token")
    return credentials.credentials


# ── Current user ───────────────────────────────────────────────────────────────

async def get_current_user_id(
    raw_token: str = Depends(get_raw_token),
) -> uuid.UUID:
    """
    Verify the Bearer JWT and return the authenticated user's UUID.

    Raises HTTP 401 if the token is invalid or expired.
    """
    return extract_user_id_from_token(raw_token)
