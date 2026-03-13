"""
Tests for POST /api/v1/auth/resend-verification

AUTH-002 – Resend email verification
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


ENDPOINT = "/api/v1/auth/resend-verification"


# ── 1. Success path ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resend_verification_success(client):
    """POST /resend-verification returns 200 with generic success message."""
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.resend_verification_email",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(ENDPOINT, json={"email": "user@example.com"})

    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body


# ── 2. Unknown email still returns 200 (anti-enumeration) ─────────────────────

@pytest.mark.asyncio
async def test_resend_verification_unknown_email_returns_200(client):
    """Even if Supabase raises an ExternalServiceError, we return 200."""
    from app.core.exceptions import ExternalServiceError

    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.resend_verification_email",
        new_callable=AsyncMock,
        side_effect=ExternalServiceError("not found"),
    ):
        resp = await client.post(ENDPOINT, json={"email": "ghost@example.com"})

    assert resp.status_code == 200


# ── 3. Invalid email → 422 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resend_verification_invalid_email(client):
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.resend_verification_email",
        new_callable=AsyncMock,
    ):
        resp = await client.post(ENDPOINT, json={"email": "not-an-email"})

    assert resp.status_code == 422


# ── 4. Missing body → 422 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resend_verification_missing_body(client):
    with patch(
        "app.api.v1.auth.supabase_client.SupabaseAuthClient.resend_verification_email",
        new_callable=AsyncMock,
    ):
        resp = await client.post(ENDPOINT, json={})

    assert resp.status_code == 422
