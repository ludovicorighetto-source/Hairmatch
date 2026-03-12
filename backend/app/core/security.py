import hashlib
import re
import uuid
from typing import Optional

from jose import ExpiredSignatureError, JWTError, jwt

from app.config import get_settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError

settings = get_settings()

# Minimum password requirements
_PASSWORD_MIN_LENGTH = 8
_PASSWORD_UPPER_RE = re.compile(r"[A-Z]")
_PASSWORD_DIGIT_RE = re.compile(r"[0-9]")
_PASSWORD_SPECIAL_RE = re.compile(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./<>?`~]')


def validate_password_strength(password: str) -> None:
    """
    Validate password complexity.

    Raises ValueError with a descriptive message if requirements are not met.
    """
    errors: list[str] = []

    if len(password) < _PASSWORD_MIN_LENGTH:
        errors.append(f"at least {_PASSWORD_MIN_LENGTH} characters")

    if not _PASSWORD_UPPER_RE.search(password):
        errors.append("at least one uppercase letter")

    if not _PASSWORD_DIGIT_RE.search(password):
        errors.append("at least one digit")

    if not _PASSWORD_SPECIAL_RE.search(password):
        errors.append("at least one special character")

    if errors:
        raise ValueError(f"Password must contain: {', '.join(errors)}")


def verify_supabase_jwt(token: str) -> dict:
    """
    Verify a Supabase-issued JWT and return its payload.

    Raises:
        ExpiredTokenError: if the token has expired.
        InvalidTokenError: if the token is malformed or the signature is wrong.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except ExpiredSignatureError:
        raise ExpiredTokenError()
    except JWTError:
        raise InvalidTokenError()


def extract_user_id_from_token(token: str) -> uuid.UUID:
    """
    Decode the JWT and return the Supabase user UUID (``sub`` claim).

    Raises:
        InvalidTokenError: if ``sub`` is missing or not a valid UUID.
        ExpiredTokenError: if the token has expired.
    """
    payload = verify_supabase_jwt(token)
    sub: Optional[str] = payload.get("sub")
    if not sub:
        raise InvalidTokenError("Token is missing 'sub' claim")
    try:
        return uuid.UUID(sub)
    except ValueError:
        raise InvalidTokenError("Token 'sub' claim is not a valid UUID")


def make_redis_refresh_key(user_id: uuid.UUID, refresh_token: str) -> str:
    """
    Build the Redis key for a refresh token.

    Format: ``refresh:{user_id}:{first16_chars_of_sha256(token)}``
    """
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()[:16]
    return f"refresh:{user_id}:{token_hash}"


def hash_token_prefix(token: str) -> str:
    """Return the first 16 hex chars of the SHA-256 of *token*."""
    return hashlib.sha256(token.encode()).hexdigest()[:16]
