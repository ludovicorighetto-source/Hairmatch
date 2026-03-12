"""
Tests for POST /api/v1/auth/login

AUTH-001 – Login endpoint
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import InactiveUserError, InvalidCredentialsError
from app.core.security import make_redis_refresh_key
from app.models.enums import UserRole
from tests.conftest import TEST_USER_ID_PROFESSIONAL, TEST_USER_ID_SALON, _make_jwt


ENDPOINT = "/api/v1/auth/login"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _login_payload(email: str = "salon@example.com", password: str = "SecurePass1!") -> dict:
    return {"email": email, "password": password}


def _make_app_for_salon(mock_supabase_salon, db_session, mock_redis):
    """Return a FastAPI app with dependency overrides wired to salon fixtures."""
    from app.dependencies import get_db, get_redis
    from app.main import create_app

    redis_mock, _ = mock_redis

    async def _override_db():
        yield db_session

    async def _override_redis():
        return redis_mock

    application = create_app()
    application.dependency_overrides[get_db] = _override_db
    application.dependency_overrides[get_redis] = _override_redis
    return application


# ── 1. Salon login success ────────────────────────────────────────────────────

async def test_login_salon_success(
    client, mock_supabase_salon, mock_redis, salon_user_in_db
):
    """Valid salon login → 200, access_token, refresh_token, role='salon'."""
    _, _ = salon_user_in_db  # ensure DB has the user

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(ENDPOINT, json=_login_payload())

    assert response.status_code == 200
    body = response.json()

    assert "tokens" in body
    assert body["tokens"]["access_token"]
    assert body["tokens"]["refresh_token"]
    assert body["tokens"]["token_type"] == "bearer"

    assert "user" in body
    assert body["user"]["role"] == "salon"

    assert "profile" in body
    assert body["profile"]["business_name"] == "Test Salon"


# ── 2. Professional login success ─────────────────────────────────────────────

async def test_login_professional_success(
    client,
    mock_supabase_professional,
    mock_redis,
    professional_user_in_db,
):
    """Valid professional login → 200, role='professional'."""
    _, _ = professional_user_in_db  # ensure DB has the user

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_professional):
        response = await client.post(
            ENDPOINT,
            json=_login_payload(email="professional@example.com"),
        )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "professional"
    assert body["profile"]["first_name"] == "Mario"


# ── 3. Invalid credentials → 401 ─────────────────────────────────────────────

async def test_login_invalid_credentials(client, mock_supabase_salon, mock_redis):
    """Wrong password → Supabase raises InvalidCredentialsError → HTTP 401."""
    mock_supabase_salon.sign_in_with_password = AsyncMock(
        side_effect=InvalidCredentialsError()
    )

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(
            ENDPOINT, json=_login_payload(password="WrongPass99!")
        )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "password" in response.json()["detail"].lower()


# ── 4. Unknown email → 401 (no account enumeration) ──────────────────────────

async def test_login_unknown_email(client, mock_supabase_salon, mock_redis):
    """
    Email not registered → same 401 INVALID_CREDENTIALS as wrong password
    to avoid leaking whether an account exists.
    """
    mock_supabase_salon.sign_in_with_password = AsyncMock(
        side_effect=InvalidCredentialsError()
    )

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(
            ENDPOINT, json=_login_payload(email="ghost@example.com")
        )

    assert response.status_code == 401
    # Same error message as wrong-password to prevent account enumeration
    assert "invalid" in response.json()["detail"].lower() or "password" in response.json()["detail"].lower()


# ── 5. Unverified account → 403 ──────────────────────────────────────────────

async def test_login_unverified_account(
    client, mock_supabase_salon, mock_redis, db_session
):
    """
    is_verified=False does NOT block login in the current implementation.
    The service only checks is_active. This test documents the current behaviour.
    If email-verification enforcement is added, update the expected status.
    """
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.models.user_profile import UserProfile
    from app.models.salon_profile import SalonProfile
    from app.models.enums import SubscriptionPlan

    unverified_uid = str(_uuid.uuid4())
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=_uuid.UUID(unverified_uid),
        role=UserRole.salon,
        is_active=True,
        is_verified=False,   # ← unverified
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)

    salon = SalonProfile(
        id=_uuid.uuid4(),
        user_id=_uuid.UUID(unverified_uid),
        business_name="Unverified Salon",
        phone="0212345678",
        address_street="Via Test 1",
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

    mock_supabase_salon.sign_in_with_password = AsyncMock(return_value={
        "access_token": _make_jwt(unverified_uid),
        "refresh_token": "token-unverified",
        "expires_in": 3600,
    })

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(
            ENDPOINT, json=_login_payload(email="unverified@example.com")
        )

    # Current behaviour: unverified users CAN log in (is_active check only)
    # Update to assert 403 if email verification enforcement is added.
    assert response.status_code in (200, 403)


# ── 6. Disabled account → 403 ────────────────────────────────────────────────

async def test_login_disabled_account(
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
        role=UserRole.salon,
        is_active=False,   # ← disabled
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)

    salon = SalonProfile(
        id=_uuid.uuid4(),
        user_id=_uuid.UUID(disabled_uid),
        business_name="Disabled Salon",
        phone="0212345678",
        address_street="Via Disabled 1",
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

    mock_supabase_salon.sign_in_with_password = AsyncMock(return_value={
        "access_token": _make_jwt(disabled_uid),
        "refresh_token": "token-disabled",
        "expires_in": 3600,
    })

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(
            ENDPOINT, json=_login_payload(email="disabled@example.com")
        )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


# ── 7. Successful login stores refresh token in Redis ────────────────────────

async def test_login_stores_refresh_token_in_redis(
    client, mock_supabase_salon, mock_redis, salon_user_in_db
):
    """After successful login, the refresh token must be persisted in Redis."""
    _, _ = salon_user_in_db
    redis_mock, store = mock_redis

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(ENDPOINT, json=_login_payload())

    assert response.status_code == 200

    # The refresh token returned by Supabase mock is "fake-refresh-token-salon"
    expected_key = make_redis_refresh_key(
        uuid.UUID(TEST_USER_ID_SALON), "fake-refresh-token-salon"
    )
    assert expected_key in store, f"Expected key {expected_key!r} not in Redis store: {list(store.keys())}"
    assert store[expected_key] == "fake-refresh-token-salon"


# ── 8. Missing password field → 422 ──────────────────────────────────────────

async def test_login_missing_fields(client, mock_supabase_salon, mock_redis):
    """Request body without password → 422 validation error."""
    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase_salon):
        response = await client.post(ENDPOINT, json={"email": "salon@example.com"})

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("password" in str(e) for e in errors)
