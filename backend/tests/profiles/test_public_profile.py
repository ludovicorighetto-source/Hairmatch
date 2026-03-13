"""
Tests for GET /api/v1/profiles/{user_id}

PROFILE-006 – Public profile view
"""

from __future__ import annotations

import uuid

import pytest


BASE = "/api/v1/profiles"


@pytest.mark.asyncio
async def test_get_public_salon_profile(client, salon_user_in_db):
    user, salon = salon_user_in_db
    resp = await client.get(f"{BASE}/{user.id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["id"] == str(user.id)
    assert body["user"]["role"] == "salon"
    assert body["profile"]["business_name"] == salon.business_name


@pytest.mark.asyncio
async def test_get_public_professional_profile(client, professional_user_in_db):
    user, pro = professional_user_in_db
    resp = await client.get(f"{BASE}/{user.id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["id"] == str(user.id)
    assert body["user"]["role"] == "professional"
    assert body["profile"]["first_name"] == pro.first_name


@pytest.mark.asyncio
async def test_get_public_profile_not_found(client):
    random_id = str(uuid.uuid4())
    resp = await client.get(f"{BASE}/{random_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_public_profile_no_auth_required(client, salon_user_in_db):
    """Public profiles don't require authentication."""
    user, _ = salon_user_in_db
    resp = await client.get(f"{BASE}/{user.id}")
    assert resp.status_code == 200
    # Sensitive fields not exposed
    body = resp.json()
    assert "is_active" not in body["user"]
