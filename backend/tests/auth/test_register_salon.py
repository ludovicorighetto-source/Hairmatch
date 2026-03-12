"""
Tests for POST /api/v1/auth/register/salon

AUTH-001 – Register Salon endpoint
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import DatabaseError, UserAlreadyExistsError
from tests.conftest import TEST_USER_ID_SALON, _make_jwt


ENDPOINT = "/api/v1/auth/register/salon"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _salon_payload(**overrides) -> dict:
    base = {
        "email": "newsalon@example.com",
        "password": "SecurePass1!",
        "business_name": "Bella Italia Salon",
        "phone": "0212345678",
        "vat_number": "99887766554",
        "address": {
            "street": "Via Verdi 42",
            "city": "Torino",
            "province": "TO",
            "postal_code": "10121",
            "country": "IT",
        },
    }
    base.update(overrides)
    return base


# ── 1. Successful registration ─────────────────────────────────────────────────

async def test_register_salon_success(client, mock_supabase, mock_redis):
    """POST /register/salon with valid data → 201 and correct response body."""
    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        response = await client.post(ENDPOINT, json=_salon_payload())

    assert response.status_code == 201
    body = response.json()

    assert "user" in body
    assert "profile" in body
    assert body["user"]["role"] == "salon"
    assert body["user"]["is_active"] is True
    assert body["profile"]["business_name"] == "Bella Italia Salon"
    assert body["profile"]["phone"] == "0212345678"
    assert "message" in body


# ── 2. Duplicate email → 409 ───────────────────────────────────────────────────

async def test_register_salon_email_duplicate(client, mock_supabase, mock_redis):
    """Supabase raises UserAlreadyExistsError when email already used → HTTP 409."""
    mock_supabase.sign_up = AsyncMock(side_effect=UserAlreadyExistsError())

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        response = await client.post(ENDPOINT, json=_salon_payload())

    assert response.status_code == 409
    detail = response.json()["detail"].lower()
    assert "already" in detail or "exist" in detail or "email" in detail


# ── 3. Duplicate VAT number → DB error + rollback ─────────────────────────────

async def test_register_salon_vat_duplicate(client, mock_supabase, mock_redis):
    """
    When the DB raises an integrity error for duplicate vat_number the service
    must call supabase.delete_user (Supabase rollback) and return 500.
    """
    # First registration – succeeds and creates the VAT
    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        r1 = await client.post(ENDPOINT, json=_salon_payload(vat_number="11111111111"))
    assert r1.status_code == 201

    # Second call: new Supabase user, same VAT → DB unique constraint fires
    second_uid = str(uuid.uuid4())
    mock_supabase.sign_up = AsyncMock(return_value={
        "user": {"id": second_uid, "email": "other2@example.com"},
        "session": {
            "access_token": _make_jwt(second_uid),
            "refresh_token": "token-dup-vat",
            "expires_in": 3600,
        },
    })

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        r2 = await client.post(ENDPOINT, json=_salon_payload(
            email="other2@example.com",
            vat_number="11111111111",   # duplicate
        ))

    # The DB unique constraint fires → DatabaseError (500) and rollback via delete_user
    assert r2.status_code == 500
    mock_supabase.delete_user.assert_called()


# ── 4. Weak password → 422 ────────────────────────────────────────────────────

async def test_register_salon_weak_password(client, mock_supabase, mock_redis):
    """Password without uppercase letter → Pydantic validator rejects with 422."""
    payload = _salon_payload(password="weakpassword1!")

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        response = await client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


# ── 5. Missing required field (business_name) → 422 ──────────────────────────

async def test_register_salon_missing_required_fields(client, mock_supabase, mock_redis):
    """Payload missing business_name → 422 validation error."""
    payload = _salon_payload()
    del payload["business_name"]

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        response = await client.post(ENDPOINT, json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("business_name" in str(e) for e in errors)


# ── 6. Invalid email → 422 ────────────────────────────────────────────────────

async def test_register_salon_invalid_email(client, mock_supabase, mock_redis):
    """Malformed email address → 422."""
    payload = _salon_payload(email="not-an-email")

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        response = await client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


# ── 7. Invalid VAT (too long) → 422 ──────────────────────────────────────────

async def test_register_salon_invalid_vat(client, mock_supabase, mock_redis):
    """VAT number exceeding max_length=20 → 422."""
    payload = _salon_payload(vat_number="A" * 21)  # 21 chars > max_length 20

    with patch("app.api.v1.auth.router.supabase_auth", mock_supabase):
        response = await client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


# ── 8. Supabase failure after DB insert triggers rollback ─────────────────────

async def test_register_salon_supabase_failure_triggers_rollback(
    db_session, mock_supabase, mock_redis
):
    """
    When the DB flush raises after Supabase user creation, the service must:
    1. Call supabase.delete_user to roll back the Supabase user.
    2. Raise DatabaseError (HTTP 500).

    We test this at the service layer to avoid brittle HTTP-level mock wiring.
    """
    import uuid as _uuid
    from app.api.v1.auth.schemas import AddressSchema, RegisterSalonRequest
    from app.api.v1.auth.service import AuthService

    redis_mock, store = mock_redis
    failing_supabase = AsyncMock()
    bad_uid = str(_uuid.uuid4())
    failing_supabase.sign_up = AsyncMock(return_value={
        "user": {"id": bad_uid, "email": "fail@example.com"},
        "session": None,
    })
    failing_supabase.delete_user = AsyncMock(return_value=None)

    # Make the DB session's flush raise after the first call
    original_flush = db_session.flush
    flush_call_count = 0

    async def _failing_flush():
        nonlocal flush_call_count
        flush_call_count += 1
        if flush_call_count >= 1:
            raise Exception("Simulated DB failure")
        await original_flush()

    db_session.flush = _failing_flush

    service = AuthService(
        db=db_session,
        redis_client=redis_mock,
        supabase=failing_supabase,
    )

    payload = RegisterSalonRequest(
        email="fail@example.com",
        password="SecurePass1!",
        business_name="Fail Salon",
        phone="0212345678",
        address=AddressSchema(
            street="Via Fail 1",
            city="Roma",
            province="RM",
            postal_code="00100",
            country="IT",
        ),
    )

    with pytest.raises(DatabaseError):
        with patch("app.core.security.settings") as ms:
            ms.SUPABASE_JWT_SECRET = "test-secret-key-for-tests-only"
            ms.ACCESS_TOKEN_EXPIRE_MINUTES = 15
            ms.refresh_token_expire_seconds = 604800
            await service.register_salon(payload)

    # Supabase rollback must have been called
    failing_supabase.delete_user.assert_called_once_with(_uuid.UUID(bad_uid))
