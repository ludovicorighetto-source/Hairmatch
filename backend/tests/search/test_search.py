"""
Tests for SEARCH-001 / SEARCH-002

GET /api/v1/search/professionals
GET /api/v1/search/salons
"""

from __future__ import annotations

import uuid

import pytest

from app.models.enums import AvailabilityStatus, SubscriptionPlan, UserRole
from app.models.professional_profile import ProfessionalProfile
from app.models.salon_profile import SalonProfile
from app.models.user_profile import UserProfile


PROF_ENDPOINT = "/api/v1/search/professionals"
SALON_ENDPOINT = "/api/v1/search/salons"


# ── Fixtures: seed complete profiles ──────────────────────────────────────────

@pytest.fixture
async def complete_professional(db_session):
    """Insert a complete, available professional."""
    user_id = uuid.uuid4()
    user = UserProfile(id=user_id, role=UserRole.professional, is_active=True, is_verified=True)
    db_session.add(user)
    await db_session.flush()

    pro = ProfessionalProfile(
        user_id=user_id,
        first_name="Marco",
        last_name="Rossi",
        phone="+39 333 1234567",
        specializations=["Colorazione", "Taglio"],
        years_of_experience=5,
        preferred_city="Milano",
        preferred_province="MI",
        availability_status=AvailabilityStatus.available,
        bio="Esperto colorista con 5 anni di esperienza",
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=True,
    )
    db_session.add(pro)
    await db_session.flush()
    await db_session.refresh(pro)
    return user, pro


@pytest.fixture
async def incomplete_professional(db_session):
    """Insert a professional without bio (incomplete profile)."""
    user_id = uuid.uuid4()
    user = UserProfile(id=user_id, role=UserRole.professional, is_active=True, is_verified=False)
    db_session.add(user)
    await db_session.flush()

    pro = ProfessionalProfile(
        user_id=user_id,
        first_name="Anna",
        last_name="Verdi",
        phone="+39 333 9999999",
        specializations=["Taglio"],
        availability_status=AvailabilityStatus.available,
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=False,  # incomplete
    )
    db_session.add(pro)
    await db_session.flush()
    return user, pro


@pytest.fixture
async def complete_salon(db_session):
    """Insert a complete salon."""
    user_id = uuid.uuid4()
    user = UserProfile(id=user_id, role=UserRole.salon, is_active=True, is_verified=True)
    db_session.add(user)
    await db_session.flush()

    salon = SalonProfile(
        user_id=user_id,
        business_name="Salone Bello",
        phone="+39 02 1234567",
        address_street="Via Roma 1",
        address_city="Milano",
        address_province="MI",
        address_postal_code="20100",
        address_country="IT",
        description="Il miglior salone di Milano",
        subscription_plan=SubscriptionPlan.free,
        is_profile_complete=True,
    )
    db_session.add(salon)
    await db_session.flush()
    await db_session.refresh(salon)
    return user, salon


# ── Search Professionals ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_professionals_returns_complete_only(
    client, complete_professional, incomplete_professional
):
    """Only professionals with is_profile_complete=True appear in results."""
    resp = await client.get(PROF_ENDPOINT)
    assert resp.status_code == 200
    body = resp.json()
    user_ids = [item["user_id"] for item in body["items"]]
    complete_user_id = str(complete_professional[0].id)
    incomplete_user_id = str(incomplete_professional[0].id)
    assert complete_user_id in user_ids
    assert incomplete_user_id not in user_ids


@pytest.mark.asyncio
async def test_search_professionals_filter_by_city(client, complete_professional):
    user, pro = complete_professional

    resp_match = await client.get(PROF_ENDPOINT, params={"city": "Milano"})
    assert resp_match.status_code == 200
    assert any(item["user_id"] == str(user.id) for item in resp_match.json()["items"])

    resp_no_match = await client.get(PROF_ENDPOINT, params={"city": "Roma"})
    assert resp_no_match.status_code == 200
    assert not any(item["user_id"] == str(user.id) for item in resp_no_match.json()["items"])


@pytest.mark.asyncio
async def test_search_professionals_filter_by_specialization(client, complete_professional):
    user, pro = complete_professional

    resp = await client.get(PROF_ENDPOINT, params={"specializations": ["Colorazione"]})
    assert resp.status_code == 200
    assert any(item["user_id"] == str(user.id) for item in resp.json()["items"])

    resp_no = await client.get(PROF_ENDPOINT, params={"specializations": ["Extension"]})
    assert resp_no.status_code == 200
    assert not any(item["user_id"] == str(user.id) for item in resp_no.json()["items"])


@pytest.mark.asyncio
async def test_search_professionals_pagination(client, complete_professional):
    resp = await client.get(PROF_ENDPOINT, params={"page": 1, "limit": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert "total" in body
    assert "pages" in body
    assert len(body["items"]) <= 1


@pytest.mark.asyncio
async def test_search_professionals_no_auth_required(client, complete_professional):
    """Search endpoint is public."""
    resp = await client.get(PROF_ENDPOINT)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search_professionals_response_structure(client, complete_professional):
    resp = await client.get(PROF_ENDPOINT)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "limit" in body
    assert "pages" in body
    if body["items"]:
        item = body["items"][0]
        assert "user_id" in item
        assert "first_name" in item
        assert "specializations" in item
        assert "availability_status" in item


# ── Search Salons ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_salons_returns_complete_only(client, complete_salon):
    resp = await client.get(SALON_ENDPOINT)
    assert resp.status_code == 200
    body = resp.json()
    user_ids = [item["user_id"] for item in body["items"]]
    assert str(complete_salon[0].id) in user_ids


@pytest.mark.asyncio
async def test_search_salons_filter_by_city(client, complete_salon):
    user, salon = complete_salon

    resp = await client.get(SALON_ENDPOINT, params={"city": "Milano"})
    assert resp.status_code == 200
    assert any(item["user_id"] == str(user.id) for item in resp.json()["items"])

    resp_no = await client.get(SALON_ENDPOINT, params={"city": "Napoli"})
    assert resp_no.status_code == 200
    assert not any(item["user_id"] == str(user.id) for item in resp_no.json()["items"])


@pytest.mark.asyncio
async def test_search_salons_no_auth_required(client, complete_salon):
    resp = await client.get(SALON_ENDPOINT)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search_salons_response_structure(client, complete_salon):
    resp = await client.get(SALON_ENDPOINT)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    if body["items"]:
        item = body["items"][0]
        assert "user_id" in item
        assert "business_name" in item
        assert "address_city" in item


@pytest.mark.asyncio
async def test_search_salons_pagination(client, complete_salon):
    resp = await client.get(SALON_ENDPOINT, params={"page": 1, "limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) <= 5


@pytest.mark.asyncio
async def test_search_salons_filter_by_province(client, complete_salon):
    user, salon = complete_salon

    resp = await client.get(SALON_ENDPOINT, params={"province": "MI"})
    assert resp.status_code == 200
    assert any(item["user_id"] == str(user.id) for item in resp.json()["items"])
