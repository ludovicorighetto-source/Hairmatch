"""
Tests for GET /api/v1/auth/me

AUTH-001 – Current user profile endpoint
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.conftest import TEST_USER_ID_PROFESSIONAL, TEST_USER_ID_SALON, _make_expired_jwt, _make_jwt


ENDPOINT = "/api/v1/auth/me"


# ── 1. Salon user – success ────────────────────────────────────────────────────

async def test_me_salon_success(
    client, mock_supabase_salon, mock_redis, authenticated_salon
):
    """Valid Bearer token for a salon user → 200 with user + salon profile."""
    access_token = authenticated_salon["access_token"]

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.get(
            ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    body = response.json()

    assert "user" in body
    assert body["user"]["role"] == "salon"
    assert body["user"]["is_active"] is True

    assert "profile" in body
    assert body["profile"]["business_name"] == "Test Salon"
    assert "user_id" in body["profile"]


# ── 2. Professional user – success ────────────────────────────────────────────

async def test_me_professional_success(
    client,
    mock_supabase_professional,
    mock_redis,
    authenticated_professional,
):
    """Valid Bearer token for a professional → 200 with user + professional profile."""
    access_token = authenticated_professional["access_token"]

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_professional):
        response = await client.get(
            ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    body = response.json()

    assert body["user"]["role"] == "professional"
    assert body["profile"]["first_name"] == "Mario"
    assert body["profile"]["last_name"] == "Rossi"


# ── 3. No Authorization header → 401 ──────────────────────────────────────────

async def test_me_no_token(client, mock_supabase_salon, mock_redis):
    """Missing Authorization header → 401."""
    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.get(ENDPOINT)

    assert response.status_code == 401


# ── 4. Expired token → 401 ────────────────────────────────────────────────────

async def test_me_expired_token(client, mock_supabase_salon, mock_redis):
    """Expired JWT → 401 TOKEN_EXPIRED."""
    expired_token = _make_expired_jwt(TEST_USER_ID_SALON)

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.get(
            ENDPOINT,
            headers={"Authorization": f"Bearer {expired_token}"},
        )

    assert response.status_code == 401
    detail = response.json()["detail"].lower()
    assert "expired" in detail or "token" in detail


# ── 5. Malformed token → 401 ──────────────────────────────────────────────────

async def test_me_malformed_token(client, mock_supabase_salon, mock_redis):
    """Malformed JWT → 401 INVALID_TOKEN."""
    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.get(
            ENDPOINT,
            headers={"Authorization": "Bearer this.is.not.a.jwt"},
        )

    assert response.status_code == 401


# ── 6. Valid token but user not in DB → 404 ──────────────────────────────────

async def test_me_user_not_in_db(client, mock_supabase_salon, mock_redis):
    """
    A valid JWT for a user_id that has no matching row in user_profiles → 404.
    """
    import uuid
    unknown_uid = str(uuid.uuid4())
    token = _make_jwt(unknown_uid)

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.get(
            ENDPOINT,
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404


# ── 7. Disabled account → 403 ────────────────────────────────────────────────

async def test_me_disabled_account(
    client, mock_supabase_salon, mock_redis, db_session
):
    """is_active=False → InactiveUserError → HTTP 403."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.models.user_profile import UserProfile
    from app.models.salon_profile import SalonProfile
    from app.models.enums import SubscriptionPlan

    disabled_uid = str(_uuid.uuid4())
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=_uuid.UUID(disabled_uid),
        role="salon",
        is_active=False,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)

    salon = SalonProfile(
        id=_uuid.uuid4(),
        user_id=_uuid.UUID(disabled_uid),
        business_name="Disabled Salon ME",
        phone="0212345678",
        address_street="Via X 1",
        address_city="Roma",
        address_province="RM",
        address_postal_code="00100",
        address_country="IT",
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=False,
        is_featured=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(salon)
    await db_session.flush()

    token = _make_jwt(disabled_uid)

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.get(
            ENDPOINT,
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()
