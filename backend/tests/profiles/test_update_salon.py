"""
Tests for PATCH /api/v1/profiles/me/salon

PROFILE-001 – Salon profile update
"""

from __future__ import annotations

import pytest


ENDPOINT = "/api/v1/profiles/me/salon"


# ── 1. Successful partial update ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_salon_description(client, salon_user_in_db, make_access_token):
    user, salon = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"description": "Il miglior salone della città"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["description"] == "Il miglior salone della città"
    # Other fields remain unchanged
    assert body["business_name"] == salon.business_name


@pytest.mark.asyncio
async def test_update_salon_multiple_fields(client, salon_user_in_db, make_access_token):
    user, salon = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={
            "phone": "+39 02 9876543",
            "seats_count": 8,
            "description": "Salone premium con 8 postazioni",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["phone"] == "+39 02 9876543"
    assert body["seats_count"] == 8
    assert body["description"] == "Salone premium con 8 postazioni"


@pytest.mark.asyncio
async def test_update_salon_coordinates(client, salon_user_in_db, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"latitude": 45.4654, "longitude": 9.1859},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["latitude"] == pytest.approx(45.4654, rel=1e-4)
    assert body["longitude"] == pytest.approx(9.1859, rel=1e-4)


@pytest.mark.asyncio
async def test_update_salon_opening_hours(client, salon_user_in_db, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    hours = {
        "monday": {"open": "09:00", "close": "19:00", "closed": False},
        "tuesday": {"open": "09:00", "close": "19:00", "closed": False},
        "sunday": None,
    }
    resp = await client.patch(
        ENDPOINT,
        json={"opening_hours": hours},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ── 2. is_profile_complete flag ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_salon_profile_becomes_complete(client, salon_user_in_db, make_access_token):
    """Adding a description to an otherwise filled profile marks it complete."""
    user, salon = salon_user_in_db
    token = make_access_token(str(user.id))

    # Salon fixture already has business_name, phone, address.
    # Just add description to trigger completion.
    resp = await client.patch(
        ENDPOINT,
        json={"description": "Descrizione completa del salone"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_profile_complete"] is True


# ── 3. Auth required ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_salon_unauthenticated(client):
    resp = await client.patch(ENDPOINT, json={"description": "test"})
    assert resp.status_code == 401


# ── 4. Professional cannot update salon profile ────────────────────────────────

@pytest.mark.asyncio
async def test_professional_cannot_update_salon(client, professional_user_in_db, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"description": "hacking"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ── 5. Empty payload → 200 (no-op) ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_salon_empty_payload(client, salon_user_in_db, make_access_token):
    """Empty PATCH is a valid no-op."""
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ── 6. Validation errors ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_salon_invalid_seats(client, salon_user_in_db, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        ENDPOINT,
        json={"seats_count": -1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
