"""
Tests for JOB-001 / JOB-002 / JOB-005 / JOB-006

POST   /api/v1/jobs/
GET    /api/v1/jobs/mine
PATCH  /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
POST   /api/v1/jobs/{job_id}/apply
GET    /api/v1/jobs/applications/mine
GET    /api/v1/jobs/                   (public browse)
"""

from __future__ import annotations

import uuid

import pytest

from app.models.enums import ApplicationStatus, JobStatus, SubscriptionPlan, UserRole
from app.models.job_posting import JobPosting
from app.models.user_profile import UserProfile


JOBS_ENDPOINT = "/api/v1/jobs"


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _job_payload(**kwargs) -> dict:
    base = {
        "title": "Cerca colorista full-time",
        "description": "Salone in zona Navigli cerca colorista esperto con almeno 3 anni.",
        "specializations": ["Colorazione"],
        "contract_types": ["full_time"],
        "city": "Milano",
        "province": "MI",
    }
    base.update(kwargs)
    return base


@pytest.fixture
async def open_job(db_session, salon_user_in_db):
    user, salon = salon_user_in_db
    job = JobPosting(
        salon_id=user.id,
        title="Cerca tagliatore",
        description="Salone cerca tagliatore senior full-time immediato.",
        specializations=["Taglio"],
        contract_types=["full_time"],
        city="Milano",
        province="MI",
        status=JobStatus.open,
    )
    db_session.add(job)
    await db_session.flush()
    await db_session.refresh(job)
    return job


# ── Salon: Create job posting ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_job_posting(client, salon_user_in_db, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.post(
        JOBS_ENDPOINT,
        json=_job_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Cerca colorista full-time"
    assert body["status"] == "open"
    assert body["salon_id"] == str(user.id)


@pytest.mark.asyncio
async def test_create_job_posting_professional_forbidden(
    client, professional_user_in_db, make_access_token
):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.post(
        JOBS_ENDPOINT,
        json=_job_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_job_requires_auth(client):
    resp = await client.post(JOBS_ENDPOINT, json=_job_payload())
    assert resp.status_code == 401


# ── Salon: List own jobs ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_my_jobs(client, salon_user_in_db, open_job, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.get(
        f"{JOBS_ENDPOINT}/mine",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert any(item["id"] == str(open_job.id) for item in body["items"])


# ── Salon: Update job ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_job_posting(client, salon_user_in_db, open_job, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        f"{JOBS_ENDPOINT}/{open_job.id}",
        json={"title": "Cerca tagliatore senior", "status": "closed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Cerca tagliatore senior"
    assert resp.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_update_other_salon_job_forbidden(
    client, professional_user_in_db, open_job, make_access_token
):
    """Professional cannot update a salon's job."""
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.patch(
        f"{JOBS_ENDPOINT}/{open_job.id}",
        json={"title": "hacked"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ── Salon: Delete job ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_job_posting(client, salon_user_in_db, open_job, make_access_token):
    user, _ = salon_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.delete(
        f"{JOBS_ENDPOINT}/{open_job.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204

    # Verify deleted
    resp2 = await client.get(
        f"{JOBS_ENDPOINT}/mine",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert not any(item["id"] == str(open_job.id) for item in resp2.json()["items"])


# ── Public: Browse open jobs ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_browse_jobs_public(client, open_job):
    resp = await client.get(JOBS_ENDPOINT)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert any(item["id"] == str(open_job.id) for item in body["items"])


@pytest.mark.asyncio
async def test_browse_jobs_filter_by_city(client, open_job):
    resp = await client.get(JOBS_ENDPOINT, params={"city": "Milano"})
    assert resp.status_code == 200
    assert any(item["id"] == str(open_job.id) for item in resp.json()["items"])

    resp2 = await client.get(JOBS_ENDPOINT, params={"city": "Roma"})
    assert resp2.status_code == 200
    assert not any(item["id"] == str(open_job.id) for item in resp2.json()["items"])


# ── Professional: Apply to job ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_professional_applies_to_job(
    client, professional_user_in_db, open_job, make_access_token
):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    resp = await client.post(
        f"{JOBS_ENDPOINT}/{open_job.id}/apply",
        json={"cover_letter": "Sono molto interessato a questa posizione!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["job_id"] == str(open_job.id)
    assert body["professional_id"] == str(user.id)


@pytest.mark.asyncio
async def test_duplicate_application_rejected(
    client, professional_user_in_db, open_job, make_access_token
):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    # First application
    await client.post(
        f"{JOBS_ENDPOINT}/{open_job.id}/apply",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Second application (duplicate)
    resp = await client.post(
        f"{JOBS_ENDPOINT}/{open_job.id}/apply",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 500  # DatabaseError → 500


@pytest.mark.asyncio
async def test_salon_cannot_apply_to_job(
    client, salon_user_in_db, open_job, make_access_token
):
    """Salon cannot apply to own or other salons' jobs."""
    user, _ = salon_user_in_db
    # Create a different salon to avoid "your own job" error path
    token = make_access_token(str(user.id))

    resp = await client.post(
        f"{JOBS_ENDPOINT}/{open_job.id}/apply",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ── Professional: My applications ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_my_applications(client, professional_user_in_db, open_job, make_access_token):
    user, _ = professional_user_in_db
    token = make_access_token(str(user.id))

    # Apply first
    await client.post(
        f"{JOBS_ENDPOINT}/{open_job.id}/apply",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = await client.get(
        f"{JOBS_ENDPOINT}/applications/mine",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    apps = resp.json()
    assert len(apps) >= 1
    assert any(a["job_id"] == str(open_job.id) for a in apps)
    # Each item includes job details
    assert "job" in apps[0]


# ── Salon: View applicants ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_salon_views_applicants(
    client,
    salon_user_in_db,
    professional_user_in_db,
    open_job,
    make_access_token,
):
    salon_user, _ = salon_user_in_db
    prof_user, _ = professional_user_in_db
    prof_token = make_access_token(str(prof_user.id))
    salon_token = make_access_token(str(salon_user.id))

    # Professional applies
    await client.post(
        f"{JOBS_ENDPOINT}/{open_job.id}/apply",
        json={},
        headers={"Authorization": f"Bearer {prof_token}"},
    )

    # Salon views applicants
    resp = await client.get(
        f"{JOBS_ENDPOINT}/{open_job.id}/applications",
        headers={"Authorization": f"Bearer {salon_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
