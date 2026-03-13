"""
Tests for PATCH /api/v1/profiles/me/professional

PROFILE-002 – Professional profile update
"""

from __future__ import annotations

import pytest


ENDPOINT = "/api/v1/profiles/me/professional"


# ── 1. Successful partial updates ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_professional_bio(client, professional_user_in_db, make_access_token):
    user, pro = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"bio": "Parrucchiere con 10 anni di esperienza nel colore"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Parrucchiere con 10 anni di esperienza nel colore"


@pytest.mark.asyncio
async def test_update_professional_specializations(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"specializations": ["Colorazione", "Taglio", "Trattamenti"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "Colorazione" in resp.json()["specializations"]


@pytest.mark.asyncio
async def test_update_professional_availability(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"availability_status": "available"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["availability_status"] == "available"


@pytest.mark.asyncio
async def test_update_professional_work_preferences(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={
            "preferred_city": "Milano",
            "preferred_province": "MI",
            "max_travel_km": 30,
            "is_available_remotely": True,
            "preferred_contract_types": ["full_time", "freelance"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["preferred_city"] == "Milano"
    assert body["max_travel_km"] == 30
    assert body["is_available_remotely"] is True


# ── 2. Profile completion flag ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_professional_profile_becomes_complete(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={
            "bio": "Professionista esperta con passione per il colore",
            "specializations": ["Colorazione"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_profile_complete"] is True


# ── 3. Auth required ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_professional_unauthenticated(client):
    resp = await client.patch(ENDPOINT, json={"bio": "test"})
    assert resp.status_code == 401


# ── 4. Salon cannot update professional profile ────────────────────────────────

@pytest.mark.asyncio
async def test_salon_cannot_update_professional(client, salon_user_in_db, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"bio": "hacking"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ── 5. Invalid availability status → 422 ──────────────────────────────────────

@pytest.mark.asyncio
async def test_update_professional_invalid_status(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"availability_status": "nonexistent_status"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


# ── 6. Invalid travel km → 422 ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_professional_invalid_travel_km(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"max_travel_km": -5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
