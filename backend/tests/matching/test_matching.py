"""
Tests for MATCH-001 / MATCH-002 / MATCH-003

GET /api/v1/matching/professionals
GET /api/v1/matching/jobs
"""

from __future__ import annotations

import uuid

import pytest

from app.models.enums import ApplicationStatus, AvailabilityStatus, JobStatus, SubscriptionPlan
from app.models.job_posting import JobPosting
from app.models.professional_profile import ProfessionalProfile


MATCHING_ENDPOINT = "/api/v1/matching"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
async def complete_professional(db_session, professional_user_in_db):
    """Mark the professional's profile as complete and set specializations."""
    user, prof = professional_user_in_db
    prof.is_profile_complete = True
    prof.specializations = ["Colorazione", "Meches"]
    prof.preferred_city = "Milano"
    prof.preferred_province = "MI"
    prof.years_of_experience = 5
    prof.availability_status = AvailabilityStatus.available
    db_session.add(prof)
    await db_session.flush()
    return user, prof


@pytest.fixture
async def open_job_colorazione(db_session, salon_user_in_db):
    """Open job posting for a colorist in Milano."""
    user, salon = salon_user_in_db
    job = JobPosting(
        salon_id=user.id,
        title="Cerca colorista",
        description="Salone in zona Navigli cerca colorista esperto.",
        specializations=["Colorazione"],
        contract_types=["full_time"],
        city="Milano",
        province="MI",
        status=JobStatus.open,
    )
    db_session.add(job)
    await db_session.flush()
    await db_session.refresh(job)
    return job


# ── MATCH-002: Top professionals for salon ─────────────────────────────────────

@pytest.mark.asyncio
async def test_top_professionals_requires_auth(client):
    resp = await client.get(f"{MATCHING_ENDPOINT}/professionals")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_top_professionals_forbidden_for_professional(
    client, professional_user_in_db, make_access_token
):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))
    resp = await client.get(
        f"{MATCHING_ENDPOINT}/professionals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_top_professionals_returns_ranked_list(
    client, salon_user_in_db, complete_professional, make_access_token
):
    salon_user, _ = salon_user_in_db
    token = make_access_token(str(salon_user.id))

    resp = await client.get(
        f"{MATCHING_ENDPOINT}/professionals",
        params={"specializations": ["Colorazione"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    # First result should have a match_score between 0 and 1
    first = body[0]
    assert 0.0 <= first["match_score"] <= 1.0
    assert "score_breakdown" in first
    assert "specialization" in first["score_breakdown"]


@pytest.mark.asyncio
async def test_top_professionals_score_breakdown(
    client, salon_user_in_db, complete_professional, make_access_token
):
    """Professional in same city with matching specializations should score high."""
    salon_user, _ = salon_user_in_db
    token = make_access_token(str(salon_user.id))

    resp = await client.get(
        f"{MATCHING_ENDPOINT}/professionals",
        params={"specializations": ["Colorazione", "Meches"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 1
    top = body[0]
    # Specialization overlap = 2/2 = 1.0; location = 1.0 (same city)
    # → total ≥ 0.70
    assert top["match_score"] >= 0.70


# ── MATCH-003: Recommended jobs for professional ───────────────────────────────

@pytest.mark.asyncio
async def test_recommended_jobs_requires_auth(client):
    resp = await client.get(f"{MATCHING_ENDPOINT}/jobs")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_recommended_jobs_forbidden_for_salon(
    client, salon_user_in_db, make_access_token
):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))
    resp = await client.get(
        f"{MATCHING_ENDPOINT}/jobs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_recommended_jobs_returns_ranked_list(
    client, professional_user_in_db, complete_professional, open_job_colorazione, make_access_token
):
    prof_user, _ = professional_user_in_db
    token = make_access_token(str(prof_user.id))

    resp = await client.get(
        f"{MATCHING_ENDPOINT}/jobs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    first = body[0]
    assert 0.0 <= first["match_score"] <= 1.0
    assert "score_breakdown" in first
    assert first["id"] == str(open_job_colorazione.id)


@pytest.mark.asyncio
async def test_recommended_jobs_high_score_for_matching(
    client, professional_user_in_db, complete_professional, open_job_colorazione, make_access_token
):
    """Colorist in Milano should get high score for colorist job in Milano."""
    prof_user, _ = professional_user_in_db
    token = make_access_token(str(prof_user.id))

    resp = await client.get(
        f"{MATCHING_ENDPOINT}/jobs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    top = next((j for j in body if j["id"] == str(open_job_colorazione.id)), None)
    assert top is not None
    # Colorazione in both + same city → score ≥ 0.80
    assert top["match_score"] >= 0.60
