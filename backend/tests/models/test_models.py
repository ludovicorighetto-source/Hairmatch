"""
Tests for SQLAlchemy models.

Verifies that models can be instantiated and persisted to the
in-memory SQLite database provided by the db_session fixture.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.enums import AvailabilityStatus, SubscriptionPlan, UserRole
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile
from app.models.user_profile import UserProfile


# ── UserProfile ────────────────────────────────────────────────────────────────

async def test_user_profile_creation(db_session):
    """UserProfile can be inserted and retrieved."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=uid,
        role=UserRole.salon,
        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    from sqlalchemy import select

    result = await db_session.execute(
        select(UserProfile).where(UserProfile.id == uid)
    )
    fetched = result.scalar_one_or_none()

    assert fetched is not None
    assert fetched.id == uid
    assert fetched.role == UserRole.salon
    assert fetched.is_active is True
    assert fetched.is_verified is False


async def test_user_profile_defaults(db_session):
    """UserProfile is_active defaults to True and is_verified to False."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=uid,
        role=UserRole.professional,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    from sqlalchemy import select

    result = await db_session.execute(
        select(UserProfile).where(UserProfile.id == uid)
    )
    fetched = result.scalar_one()
    assert fetched.is_active is True
    assert fetched.is_verified is False


async def test_user_profile_repr(db_session):
    """UserProfile __repr__ contains id and role."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)
    user = UserProfile(
        id=uid,
        role=UserRole.salon,
        created_at=now,
        updated_at=now,
    )
    r = repr(user)
    assert str(uid) in r
    assert "salon" in r


# ── SalonProfile ───────────────────────────────────────────────────────────────

async def test_salon_profile_creation(db_session):
    """SalonProfile can be inserted with all required fields."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=uid,
        role=UserRole.salon,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    salon_id = uuid.uuid4()
    salon = SalonProfile(
        id=salon_id,
        user_id=uid,
        business_name="Model Test Salon",
        phone="0212345678",
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

    from sqlalchemy import select

    result = await db_session.execute(
        select(SalonProfile).where(SalonProfile.id == salon_id)
    )
    fetched = result.scalar_one()

    assert fetched.user_id == uid
    assert fetched.business_name == "Model Test Salon"
    assert fetched.address_city == "Milano"
    assert fetched.subscription_plan == SubscriptionPlan.free


async def test_salon_profile_optional_fields(db_session):
    """SalonProfile optional fields default to None."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=uid,
        role=UserRole.salon,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    salon = SalonProfile(
        id=uuid.uuid4(),
        user_id=uid,
        business_name="Minimal Salon",
        phone="0212345678",
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

    assert salon.vat_number is None
    assert salon.website_url is None
    assert salon.description is None
    assert salon.logo_url is None


async def test_salon_profile_repr(db_session):
    """SalonProfile __repr__ contains id and business_name."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(id=uid, role=UserRole.salon, created_at=now, updated_at=now)
    db_session.add(user)
    await db_session.flush()

    salon_id = uuid.uuid4()
    salon = SalonProfile(
        id=salon_id,
        user_id=uid,
        business_name="ReprTest",
        phone="0212345678",
        address_street="Via X",
        address_city="City",
        address_province="CI",
        address_postal_code="00000",
        address_country="IT",
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=False,
        is_featured=False,
        created_at=now,
        updated_at=now,
    )
    r = repr(salon)
    assert "ReprTest" in r


# ── ProfessionalProfile ────────────────────────────────────────────────────────

async def test_professional_profile_creation(db_session):
    """ProfessionalProfile can be inserted with all required fields."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=uid,
        role=UserRole.professional,
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    pro_id = uuid.uuid4()
    professional = ProfessionalProfile(
        id=pro_id,
        user_id=uid,
        first_name="Laura",
        last_name="Verdi",
        phone="3391234567",
        specializations=["haircutting"],
        max_travel_km=10,
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

    from sqlalchemy import select

    result = await db_session.execute(
        select(ProfessionalProfile).where(ProfessionalProfile.id == pro_id)
    )
    fetched = result.scalar_one()

    assert fetched.user_id == uid
    assert fetched.first_name == "Laura"
    assert fetched.last_name == "Verdi"
    assert "haircutting" in fetched.specializations
    assert fetched.availability_status == AvailabilityStatus.available


async def test_professional_profile_optional_fields(db_session):
    """ProfessionalProfile optional fields default to None."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(
        id=uid,
        role=UserRole.professional,
        created_at=now,
        updated_at=now,
    )
    db_session.add(user)
    await db_session.flush()

    professional = ProfessionalProfile(
        id=uuid.uuid4(),
        user_id=uid,
        first_name="Test",
        last_name="User",
        phone="3391234567",
        specializations=[],
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

    assert professional.bio is None
    assert professional.preferred_city is None
    assert professional.preferred_province is None
    assert professional.profile_photo_url is None
    assert professional.date_of_birth is None
    assert professional.years_of_experience is None


async def test_professional_profile_repr(db_session):
    """ProfessionalProfile __repr__ contains first and last name."""
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user = UserProfile(id=uid, role=UserRole.professional, created_at=now, updated_at=now)
    db_session.add(user)
    await db_session.flush()

    pro = ProfessionalProfile(
        id=uuid.uuid4(),
        user_id=uid,
        first_name="Repr",
        last_name="Test",
        phone="3391234567",
        specializations=[],
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
    r = repr(pro)
    assert "Repr" in r
    assert "Test" in r


# ── Enum values ────────────────────────────────────────────────────────────────

def test_user_role_enum_values():
    """UserRole enum contains expected string values."""
    assert UserRole.salon == "salon"
    assert UserRole.professional == "professional"


def test_subscription_plan_enum_values():
    """SubscriptionPlan enum contains expected string values."""
    assert SubscriptionPlan.free == "free"
    assert SubscriptionPlan.basic == "basic"
    assert SubscriptionPlan.premium == "premium"
    assert SubscriptionPlan.enterprise == "enterprise"


def test_availability_status_enum_values():
    """AvailabilityStatus enum contains expected string values."""
    assert AvailabilityStatus.available == "available"
    assert AvailabilityStatus.partially_available == "partially_available"
    assert AvailabilityStatus.not_available == "not_available"
    assert AvailabilityStatus.on_leave == "on_leave"
