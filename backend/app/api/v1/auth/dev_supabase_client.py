"""
Dev-mode Supabase auth client.

When DEV_MODE=true this client replaces the real Supabase client and handles
auth entirely locally – no network calls, no Supabase account needed.

Credentials are persisted to ``dev_auth_store.json`` in the backend root so
they survive server restarts.

!! NEVER USE IN PRODUCTION !!
"""

from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jose import jwt

from app.api.v1.auth.supabase_client import SupabaseAuthClient
from app.config import get_settings
from app.core.exceptions import ExternalServiceError, InvalidCredentialsError, UserAlreadyExistsError

settings = get_settings()

# Persisted store file (gitignored)
_STORE_PATH = Path(__file__).parent.parent.parent.parent.parent / "dev_auth_store.json"


def _load_store() -> dict:
    if _STORE_PATH.exists():
        try:
            return json.loads(_STORE_PATH.read_text())
        except Exception:
            pass
    return {"users": {}, "refresh_tokens": {}}


def _save_store(store: dict) -> None:
    _STORE_PATH.write_text(json.dumps(store, indent=2))


def _hash_password(password: str) -> str:
    """Simple SHA-256 hash – acceptable for dev-only use."""
    return hashlib.sha256(password.encode()).hexdigest()


def _sign_jwt(user_id: str, email: str = "", role: str = "") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        ),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class DevSupabaseAuthClient(SupabaseAuthClient):
    """Local auth backend for development – bypasses Supabase entirely."""

    # ── Sign up ────────────────────────────────────────────────────────────────

    async def sign_up(self, email: str, password: str) -> dict[str, Any]:
        store = _load_store()
        if email in store["users"]:
            raise UserAlreadyExistsError()

        user_id = str(uuid.uuid4())
        store["users"][email] = {
            "id": user_id,
            "password_hash": _hash_password(password),
            "role": "",  # filled in by set_user_role after DB insert
        }
        refresh_token = secrets.token_urlsafe(32)
        store["refresh_tokens"][refresh_token] = {"user_id": user_id, "email": email}
        _save_store(store)

        access_token = _sign_jwt(user_id, email)
        return {
            "user": {"id": user_id},
            "session": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
        }

    # ── Sign in ────────────────────────────────────────────────────────────────

    async def sign_in_with_password(self, email: str, password: str) -> dict[str, Any]:
        store = _load_store()
        record = store["users"].get(email)
        if not record or record["password_hash"] != _hash_password(password):
            raise InvalidCredentialsError()

        refresh_token = secrets.token_urlsafe(32)
        store["refresh_tokens"][refresh_token] = {"user_id": record["id"], "email": email}
        _save_store(store)

        access_token = _sign_jwt(record["id"], email, record.get("role", ""))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    # ── Refresh ────────────────────────────────────────────────────────────────

    async def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        store = _load_store()
        entry = store["refresh_tokens"].get(refresh_token)
        if not entry:
            raise ExternalServiceError("Dev mode: invalid or expired refresh token")

        user_id = entry["user_id"]
        email = entry["email"]

        # Look up role from users dict
        record = next(
            (u for u in store["users"].values() if u["id"] == user_id), None
        )
        role = record.get("role", "") if record else ""

        new_access_token = _sign_jwt(user_id, email, role)
        new_refresh_token = secrets.token_urlsafe(32)

        del store["refresh_tokens"][refresh_token]
        store["refresh_tokens"][new_refresh_token] = {"user_id": user_id, "email": email}
        _save_store(store)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    # ── Sign out ───────────────────────────────────────────────────────────────

    async def sign_out(self, access_token: str) -> None:
        pass  # No-op in dev mode

    # ── Delete user ────────────────────────────────────────────────────────────

    async def delete_user(self, user_id: uuid.UUID) -> None:
        pass  # No-op in dev mode

    # ── Role update (called post-registration) ─────────────────────────────────

    def set_user_role(self, email: str, role: str) -> None:
        """Persist the user's role so future JWTs include it."""
        store = _load_store()
        if email in store["users"]:
            store["users"][email]["role"] = role
            _save_store(store)
