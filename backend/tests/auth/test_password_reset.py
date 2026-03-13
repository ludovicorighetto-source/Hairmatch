"""
Tests for AUTH-003 – Password Reset flow

POST /api/v1/auth/request-password-reset
POST /api/v1/auth/reset-password
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


REQUEST_ENDPOINT = "/api/v1/auth/request-password-reset"
RESET_ENDPOINT = "/api/v1/auth/reset-password"


# ── Request password reset ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_request_password_reset_success(client):
    """Returns 200 with a generic message."""
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.send_password_reset_email",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(REQUEST_ENDPOINT, json={"email": "user@example.com"})

    assert resp.status_code == 200
    assert "message" in resp.json()


@pytest.mark.asyncio
async def test_request_password_reset_unknown_email_returns_200(client):
    """Anti-enumeration: unknown email still returns 200."""
    from app.core.exceptions import ExternalServiceError

    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.send_password_reset_email",
        new_callable=AsyncMock,
        side_effect=ExternalServiceError("not found"),
    ):
        resp = await client.post(REQUEST_ENDPOINT, json={"email": "ghost@example.com"})

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_request_password_reset_invalid_email(client):
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.send_password_reset_email",
        new_callable=AsyncMock,
    ):
        resp = await client.post(REQUEST_ENDPOINT, json={"email": "bad"})

    assert resp.status_code == 422


# ── Reset password ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reset_password_success(client):
    """Valid recovery token + strong password → 200."""
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.update_user_password",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            RESET_ENDPOINT,
            json={"access_token": "fake-recovery-token", "new_password": "NewPass1!"},
        )

    assert resp.status_code == 200
    assert "message" in resp.json()


@pytest.mark.asyncio
async def test_reset_password_weak_password(client):
    """Weak password → 422 (validation before Supabase call)."""
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.update_user_password",
        new_callable=AsyncMock,
    ):
        resp = await client.post(
            RESET_ENDPOINT,
            json={"access_token": "token", "new_password": "weak"},
        )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_reset_password_supabase_error(client):
    """Supabase rejects the token → 502."""
    from app.core.exceptions import ExternalServiceError

    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.update_user_password",
        new_callable=AsyncMock,
        side_effect=ExternalServiceError("invalid token"),
    ):
        resp = await client.post(
            RESET_ENDPOINT,
            json={"access_token": "bad-token", "new_password": "NewPass1!"},
        )

    assert resp.status_code == 502
