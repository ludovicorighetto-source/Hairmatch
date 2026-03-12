"""
Shared pytest fixtures for AUTH-001 test suite.

All external dependencies (Supabase, Redis, PostgreSQL) are fully mocked.
No real connections are made during tests.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import event, types
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.enums import AvailabilityStatus, SubscriptionPlan, UserRole
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile
from app.models.user_profile import UserProfile


# ── SQLite UUID type adapter ────────────────────────────────────────────────────

class SQLiteUUID(types.TypeDecorator):
    """Store UUID as a VARCHAR(36) string in SQLite."""

    impl = types.String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return uuid.UUID(value)
        except (ValueError, AttributeError):
            return value

# ── JWT helpers ─────────────────────────────────────────────────────────────────

TEST_JWT_SECRET = "test-secret-key-for-tests-only"
TEST_USER_ID_SALON = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TEST_USER_ID_PROFESSIONAL = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


def _make_jwt(
    user_id: str,
    secret: str = TEST_JWT_SECRET,
    exp_offset: int = 3600,
) -> str:
    """Generate a HS256 JWT with the given user_id as sub claim."""
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + exp_offset,
        "role": "authenticated",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _make_expired_jwt(user_id: str, secret: str = TEST_JWT_SECRET) -> str:
    """Generate an already-expired JWT."""
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iat": now - 7200,
        "exp": now - 3600,
        "role": "authenticated",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


# ── In-memory SQLite engine ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_engine():
    """Create a fresh in-memory SQLite engine per test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # SQLite does not have PostgreSQL-specific types; patch them
    async with engine.begin() as conn:
        # Register SQLite-compatible type rendering for enums
        await conn.run_sync(_create_tables)

    yield engine
    await engine.dispose()


class SQLiteArrayJSON(types.TypeDecorator):
    """
    Store a Python list as a JSON-encoded string in SQLite.
    Always returns a list on read (even if stored as null/empty).
    """

    impl = types.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        import json
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        import json
        if value is None:
            return []
        try:
            result = json.loads(value)
            if isinstance(result, list):
                return result
            return []
        except (ValueError, TypeError):
            return []


def _create_tables(conn):
    """Create all tables using SQLite-compatible metadata."""
    import sqlalchemy as sa

    # Patch column types that SQLite doesn't support
    for table in Base.metadata.tables.values():
        for col in table.columns:
            # PostgreSQL UUID → SQLite VARCHAR with Python UUID conversion
            if col.type.__class__.__name__ == "UUID":
                col.type = SQLiteUUID()
            # PostgreSQL Enum → VARCHAR
            elif isinstance(col.type, sa.Enum):
                col.type = sa.String(50)
            # PostgreSQL ARRAY → list-aware JSON text
            elif col.type.__class__.__name__ == "ARRAY":
                col.type = SQLiteArrayJSON()
            # PostgreSQL JSONB → JSON
            elif col.type.__class__.__name__ == "JSONB":
                col.type = sa.JSON()
            # PostgreSQL Numeric → Float
            elif col.type.__class__.__name__ == "Numeric":
                col.type = sa.Float()

    Base.metadata.create_all(conn)


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLAlchemy session backed by in-memory SQLite."""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


# ── Mock Supabase ──────────────────────────────────────────────────────────────

@pytest.fixture
def mock_supabase_salon():
    """Supabase mock that simulates a successful salon signup."""
    mock = AsyncMock()
    mock.sign_up = AsyncMock(return_value={
        "user": {"id": TEST_USER_ID_SALON, "email": "salon@test.com"},
        "session": {
            "access_token": _make_jwt(TEST_USER_ID_SALON),
            "refresh_token": "fake-refresh-token-salon",
            "expires_in": 3600,
        },
    })
    mock.sign_in_with_password = AsyncMock(return_value={
        "access_token": _make_jwt(TEST_USER_ID_SALON),
        "refresh_token": "fake-refresh-token-salon",
        "expires_in": 3600,
    })
    mock.sign_out = AsyncMock(return_value=None)
    mock.refresh_session = AsyncMock(return_value={
        "access_token": _make_jwt(TEST_USER_ID_SALON),
        "refresh_token": "new-refresh-token-salon",
        "expires_in": 3600,
    })
    mock.delete_user = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_supabase_professional():
    """Supabase mock that simulates a successful professional signup."""
    mock = AsyncMock()
    mock.sign_up = AsyncMock(return_value={
        "user": {"id": TEST_USER_ID_PROFESSIONAL, "email": "professional@test.com"},
        "session": {
            "access_token": _make_jwt(TEST_USER_ID_PROFESSIONAL),
            "refresh_token": "fake-refresh-token-professional",
            "expires_in": 3600,
        },
    })
    mock.sign_in_with_password = AsyncMock(return_value={
        "access_token": _make_jwt(TEST_USER_ID_PROFESSIONAL),
        "refresh_token": "fake-refresh-token-professional",
        "expires_in": 3600,
    })
    mock.sign_out = AsyncMock(return_value=None)
    mock.refresh_session = AsyncMock(return_value={
        "access_token": _make_jwt(TEST_USER_ID_PROFESSIONAL),
        "refresh_token": "new-refresh-token-professional",
        "expires_in": 3600,
    })
    mock.delete_user = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_supabase(mock_supabase_salon):
    """Default Supabase mock (salon)."""
    return mock_supabase_salon


# ── Mock Redis ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_redis():
    """
    In-memory Redis mock using a plain dict as the backing store.

    Returns (redis_mock, store_dict) so tests can inspect the store directly.
    """
    store: dict[str, Any] = {}
    redis = AsyncMock()

    async def _set(k, v, ex=None):
        store[k] = v

    async def _setex(k, ttl, v):
        store[k] = v

    async def _get(k):
        return store.get(k)

    async def _delete(*keys):
        for k in keys:
            store.pop(k, None)

    async def _exists(*keys):
        return sum(1 for k in keys if k in store)

    redis.set = AsyncMock(side_effect=_set)
    redis.setex = AsyncMock(side_effect=_setex)
    redis.get = AsyncMock(side_effect=_get)
    redis.delete = AsyncMock(side_effect=_delete)
    redis.exists = AsyncMock(side_effect=_exists)

    return redis, store


# ── App + HTTP client ──────────────────────────────────────────────────────────

@pytest.fixture
def app_with_overrides(db_session, mock_redis, mock_supabase):
    """
    Return a FastAPI app instance with dependency overrides:
    - DB → in-memory SQLite session
    - Redis → in-memory mock
    - Supabase → AsyncMock
    """
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


@pytest.fixture
async def client(app_with_overrides) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client bound to the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app_with_overrides),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Request payload fixtures ───────────────────────────────────────────────────

@pytest.fixture
def salon_user_data() -> dict:
    return {
        "email": "salon@example.com",
        "password": "SecurePass1!",
        "business_name": "Test Salon SRL",
        "phone": "0612345678",
        "vat_number": "12345678901",
        "address": {
            "street": "Via Roma 1",
            "city": "Milano",
            "province": "MI",
            "postal_code": "20100",
            "country": "IT",
        },
    }


@pytest.fixture
def professional_user_data() -> dict:
    return {
        "email": "professional@example.com",
        "password": "SecurePass1!",
        "first_name": "Mario",
        "last_name": "Rossi",
        "phone": "3331234567",
        "specializations": ["haircutting", "coloring"],
        "years_of_experience": 5,
        "preferred_city": "Roma",
        "preferred_province": "RM",
    }


# ── Pre-populated DB fixtures ──────────────────────────────────────────────────

@pytest.fixture
async def salon_user_in_db(db_session) -> tuple[UserProfile, SalonProfile]:
    """Insert a salon UserProfile + SalonProfile into the in-memory DB."""
    user_id = uuid.UUID(TEST_USER_ID_SALON)
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=user_id,
        role=UserRole.salon,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    salon = SalonProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        business_name="Test Salon",
        phone="0612345678",
        vat_number="12345678901",
        address_street="Via Roma 1",
        address_city="Milano",
        address_province="MI",
        address_postal_code="20100",
        address_country="IT",
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=False,
        is_featured=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(salon)
    await db_session.flush()

    return user, salon


@pytest.fixture
async def professional_user_in_db(db_session) -> tuple[UserProfile, ProfessionalProfile]:
    """Insert a professional UserProfile + ProfessionalProfile into the in-memory DB."""
    user_id = uuid.UUID(TEST_USER_ID_PROFESSIONAL)
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=user_id,
        role=UserRole.professional,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    professional = ProfessionalProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        first_name="Mario",
        last_name="Rossi",
        phone="3331234567",
        specializations=["haircutting"],
        max_travel_km=0,
        is_available_remotely=False,
        preferred_contract_types=[],
        availability_status=AvailabilityStatus.available,
        portfolio_urls=[],
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=False,
        is_featured=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(professional)
    await db_session.flush()

    return user, professional


@pytest.fixture
async def authenticated_salon(
    app_with_overrides,
    db_session,
    mock_supabase_salon,
    mock_redis,
    salon_user_in_db,
) -> dict:
    """
    Return auth context for a pre-existing salon user:
    - access_token: valid JWT
    - refresh_token: stored in mock Redis
    - user_id: the UUID string
    """
    from app.core.security import make_redis_refresh_key

    user, salon = salon_user_in_db
    access_token = _make_jwt(str(user.id))
    refresh_token = "salon-refresh-token-valid"

    redis_mock, store = mock_redis
    key = make_redis_refresh_key(user.id, refresh_token)
    store[key] = refresh_token

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user.id),
        "user": user,
        "salon": salon,
    }


@pytest.fixture
async def authenticated_professional(
    app_with_overrides,
    db_session,
    mock_supabase_professional,
    mock_redis,
    professional_user_in_db,
) -> dict:
    """
    Return auth context for a pre-existing professional user:
    - access_token: valid JWT
    - refresh_token: stored in mock Redis
    - user_id: the UUID string
    """
    from app.core.security import make_redis_refresh_key

    user, professional = professional_user_in_db
    access_token = _make_jwt(str(user.id))
    refresh_token = "professional-refresh-token-valid"

    redis_mock, store = mock_redis
    key = make_redis_refresh_key(user.id, refresh_token)
    store[key] = refresh_token

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user.id),
        "user": user,
        "professional": professional,
    }


# ── Patch settings to use test JWT secret ─────────────────────────────────────

@pytest.fixture(autouse=True)
def patch_settings():
    """
    Patch the app settings so JWT verification uses our TEST_JWT_SECRET.
    Also points DATABASE_URL to SQLite so database.py doesn't try PostgreSQL.
    """
    with patch("app.core.security.settings") as mock_settings:
        mock_settings.SUPABASE_JWT_SECRET = TEST_JWT_SECRET
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 15
        mock_settings.refresh_token_expire_seconds = 604800
        yield mock_settings


# ── Expose token helpers to tests ──────────────────────────────────────────────

@pytest.fixture
def make_access_token():
    """Factory fixture: returns a function that generates valid JWTs."""
    return _make_jwt


@pytest.fixture
def make_expired_token():
    """Factory fixture: returns a function that generates expired JWTs."""
    return _make_expired_jwt
