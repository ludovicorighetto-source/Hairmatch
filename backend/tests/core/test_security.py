"""
Tests for app/core/security.py

Covers:
- validate_password_strength()
- make_redis_refresh_key()
- verify_supabase_jwt() / extract_user_id_from_token()
"""

from __future__ import annotations

import hashlib
import time
import uuid
from unittest.mock import patch

import pytest
from jose import jwt

from app.core.exceptions import ExpiredTokenError, InvalidTokenError
from app.core.security import (
    extract_user_id_from_token,
    make_redis_refresh_key,
    validate_password_strength,
    verify_supabase_jwt,
)

TEST_SECRET = "test-secret-key-for-tests-only"


# ── validate_password_strength ────────────────────────────────────────────────

def test_password_too_short():
    """Password shorter than 8 characters → ValueError."""
    with pytest.raises(ValueError, match="characters"):
        validate_password_strength("Ab1!")


def test_password_no_uppercase():
    """Password with no uppercase letter → ValueError."""
    with pytest.raises(ValueError, match="uppercase"):
        validate_password_strength("weakpass1!")


def test_password_no_digit():
    """Password with no digit → ValueError."""
    with pytest.raises(ValueError, match="digit"):
        validate_password_strength("WeakPass!")


def test_password_no_special():
    """Password with no special character → ValueError."""
    with pytest.raises(ValueError, match="special"):
        validate_password_strength("WeakPass1")


def test_password_valid():
    """Compliant password → no exception raised."""
    # Should not raise
    validate_password_strength("SecurePass1!")


def test_password_valid_various_specials():
    """Multiple different special characters are all accepted."""
    for special in "!@#$%^&*()_+-=":
        validate_password_strength(f"ValidPass1{special}")


def test_password_exactly_minimum_length():
    """Password of exactly 8 characters meeting all criteria → valid."""
    validate_password_strength("Abc1!xyz")


def test_password_multiple_errors_reported():
    """Password missing multiple criteria → ValueError lists all issues."""
    with pytest.raises(ValueError) as exc_info:
        validate_password_strength("short")
    msg = str(exc_info.value).lower()
    # At least one of the missing criteria should be mentioned
    assert any(word in msg for word in ("character", "uppercase", "digit", "special"))


# ── make_redis_refresh_key ────────────────────────────────────────────────────

def test_redis_key_format():
    """make_redis_refresh_key produces 'refresh:{user_id}:{16-hex-chars}'."""
    uid = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    token = "some-refresh-token"

    key = make_redis_refresh_key(uid, token)

    parts = key.split(":")
    assert parts[0] == "refresh"
    assert parts[1] == str(uid)
    # Hash suffix is first 16 hex chars of SHA-256
    expected_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
    assert parts[2] == expected_hash


def test_redis_key_deterministic():
    """Same user_id + token always produces the same key."""
    uid = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    token = "deterministic-token"

    key1 = make_redis_refresh_key(uid, token)
    key2 = make_redis_refresh_key(uid, token)

    assert key1 == key2


def test_redis_key_different_tokens_produce_different_keys():
    """Different tokens produce different keys for the same user_id."""
    uid = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")

    key1 = make_redis_refresh_key(uid, "token-alpha")
    key2 = make_redis_refresh_key(uid, "token-beta")

    assert key1 != key2


def test_redis_key_different_users_produce_different_keys():
    """Same token for different user IDs produces different keys."""
    token = "shared-token"
    uid1 = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    uid2 = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

    key1 = make_redis_refresh_key(uid1, token)
    key2 = make_redis_refresh_key(uid2, token)

    assert key1 != key2


def test_redis_key_hash_length():
    """The hash part of the Redis key is exactly 16 hex characters."""
    uid = uuid.uuid4()
    key = make_redis_refresh_key(uid, "any-token")
    hash_part = key.split(":")[-1]
    assert len(hash_part) == 16
    assert all(c in "0123456789abcdef" for c in hash_part)


# ── verify_supabase_jwt ────────────────────────────────────────────────────────

def _make_jwt_for_test(
    user_id: str,
    secret: str = TEST_SECRET,
    exp_offset: int = 3600,
) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": user_id, "iat": now, "exp": now + exp_offset, "role": "authenticated"},
        secret,
        algorithm="HS256",
    )


def test_verify_supabase_jwt_valid():
    """Valid JWT → returns payload dict containing 'sub'."""
    token = _make_jwt_for_test("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        payload = verify_supabase_jwt(token)

    assert payload["sub"] == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def test_verify_supabase_jwt_expired():
    """Expired JWT → ExpiredTokenError."""
    now = int(time.time())
    expired_token = jwt.encode(
        {"sub": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "iat": now - 7200, "exp": now - 3600},
        TEST_SECRET,
        algorithm="HS256",
    )

    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        with pytest.raises(ExpiredTokenError):
            verify_supabase_jwt(expired_token)


def test_verify_supabase_jwt_invalid_signature():
    """JWT signed with wrong secret → InvalidTokenError."""
    token = _make_jwt_for_test("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", secret="wrong-secret")

    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        with pytest.raises(InvalidTokenError):
            verify_supabase_jwt(token)


def test_verify_supabase_jwt_malformed():
    """Completely malformed token → InvalidTokenError."""
    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        with pytest.raises(InvalidTokenError):
            verify_supabase_jwt("not.a.jwt")


# ── extract_user_id_from_token ─────────────────────────────────────────────────

def test_extract_user_id_valid():
    """Valid JWT with UUID sub → returns uuid.UUID."""
    uid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    token = _make_jwt_for_test(uid)

    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        result = extract_user_id_from_token(token)

    assert isinstance(result, uuid.UUID)
    assert str(result) == uid


def test_extract_user_id_missing_sub():
    """JWT without sub claim → InvalidTokenError."""
    now = int(time.time())
    token_no_sub = jwt.encode(
        {"iat": now, "exp": now + 3600},  # no 'sub'
        TEST_SECRET,
        algorithm="HS256",
    )

    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        with pytest.raises(InvalidTokenError):
            extract_user_id_from_token(token_no_sub)


def test_extract_user_id_invalid_uuid_sub():
    """JWT with non-UUID sub claim → InvalidTokenError."""
    now = int(time.time())
    token_bad_sub = jwt.encode(
        {"sub": "not-a-uuid", "iat": now, "exp": now + 3600},
        TEST_SECRET,
        algorithm="HS256",
    )

    with patch("app.core.security.settings") as ms:
        ms.SUPABASE_JWT_SECRET = TEST_SECRET
        with pytest.raises(InvalidTokenError):
            extract_user_id_from_token(token_bad_sub)
