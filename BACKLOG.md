# HairMatch — Product Backlog

> Platform for matching hair salons with freelance/employed professionals.
> Stack: FastAPI + PostgreSQL + Redis + Supabase Auth | Next.js 14 + TypeScript + Tailwind

---

## Legend
- ✅ Done  🔄 In Progress  🔲 To Do  ⏸ Blocked

---

## EPIC 1 — Authentication & Identity

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| AUTH-001 | Register/Login/Logout/Refresh/Me | P0 | ✅ Done | Full flow, rate limiting, JWT rotation |
| AUTH-002 | Email verification (resend endpoint) | P0 | 🔲 | Backend missing `/resend-verification`; frontend already calls it |
| AUTH-003 | Password reset flow | P1 | 🔲 | POST /request-reset + POST /reset-password + UI |
| AUTH-004 | OAuth Google login | P2 | 🔲 | Supabase OAuth, role selection post-login |

---

## EPIC 2 — Profile Management

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| PROFILE-001 | Salon profile update (PATCH) | P0 | 🔲 | Update business info, hours, location, description |
| PROFILE-002 | Professional profile update (PATCH) | P0 | 🔲 | Update bio, specializations, availability, contract prefs |
| PROFILE-003 | Profile photo & logo upload | P1 | 🔲 | Supabase Storage, presigned URLs, backend endpoint |
| PROFILE-004 | Profile completion tracking | P1 | 🔲 | is_profile_complete flag logic + onboarding wizard UI |
| PROFILE-005 | Opening hours editor (salon) | P1 | 🔲 | JSONB format, day/time pickers, frontend component |
| PROFILE-006 | Public profile page (read-only) | P1 | 🔲 | GET /salons/{id} + GET /professionals/{id} + UI |

---

## EPIC 3 — Search & Discovery

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| SEARCH-001 | Search professionals (backend) | P0 | 🔲 | Filter: city, province, specializations, availability, radius |
| SEARCH-002 | Search salons (backend) | P0 | 🔲 | Filter: city, specialization needs, subscription |
| SEARCH-003 | Search UI — professional card listing | P0 | 🔲 | Salon dashboard "Cerca professionisti" |
| SEARCH-004 | Search UI — salon card listing | P1 | 🔲 | Professional dashboard "Cerca lavoro" |
| SEARCH-005 | Geolocation search (within km radius) | P1 | 🔲 | PostGIS or Haversine formula in SQL |
| SEARCH-006 | Search filters & sorting UI | P1 | 🔲 | Sidebar filters, sort by relevance/distance/experience |

---

## EPIC 4 — Job Postings

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| JOB-001 | Job posting model & migrations | P0 | 🔲 | Title, description, specializations, salary, contract type |
| JOB-002 | CRUD job postings (backend) | P0 | 🔲 | Salon creates/edits/deletes postings; list active ones |
| JOB-003 | Job posting UI (salon) | P0 | 🔲 | "Pubblica annuncio" form + listing in salon dashboard |
| JOB-004 | Browse job postings (professional) | P0 | 🔲 | List + filter + detail page |
| JOB-005 | Job applications model | P1 | 🔲 | Professional applies to a posting (status: pending/accepted/rejected) |
| JOB-006 | Applications management (salon) | P1 | 🔲 | View applicants per posting, accept/reject |
| JOB-007 | Application status UI (professional) | P1 | 🔲 | My applications list + status badges |

---

## EPIC 5 — AI Matching

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| MATCH-001 | Matching score algorithm | P1 | 🔲 | Score = specialization overlap + location + experience + availability |
| MATCH-002 | "Top matches" endpoint for salons | P1 | 🔲 | GET /matching/professionals?salon_id=... → ranked list |
| MATCH-003 | "Recommended jobs" endpoint for professionals | P1 | 🔲 | GET /matching/jobs?professional_id=... → ranked list |
| MATCH-004 | Matching UI (salon dashboard) | P1 | 🔲 | "I tuoi match" section with ranked professional cards |
| MATCH-005 | AI-powered matching (Claude API) | P2 | 🔲 | LLM re-ranking using bio + description semantic similarity |

---

## EPIC 6 — Messaging

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| MSG-001 | Conversation & message models | P1 | 🔲 | Conversations between salon ↔ professional |
| MSG-002 | Messaging API (REST) | P1 | 🔲 | POST /messages, GET /conversations, GET /conversations/{id}/messages |
| MSG-003 | Real-time messaging (WebSocket) | P2 | 🔲 | FastAPI WebSocket endpoint + Redis pub/sub |
| MSG-004 | Messaging UI | P1 | 🔲 | Inbox, thread view, send message |

---

## EPIC 7 — Subscription & Payments

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| SUB-001 | Subscription plan enforcement | P1 | 🔲 | Feature gating based on plan (free/basic/premium/enterprise) |
| SUB-002 | Stripe integration (backend) | P2 | 🔲 | Checkout session, webhooks, subscription management |
| SUB-003 | Pricing page & upgrade flow (frontend) | P2 | 🔲 | Plan comparison table, Stripe Checkout redirect |

---

## EPIC 8 — Notifications

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| NOTIF-001 | In-app notifications model | P2 | 🔲 | New match, new message, application update |
| NOTIF-002 | Notification API | P2 | 🔲 | GET /notifications, PATCH /notifications/{id}/read |
| NOTIF-003 | Email notifications (Supabase/Resend) | P2 | 🔲 | Transactional emails for key events |
| NOTIF-004 | Notification bell UI | P2 | 🔲 | Header dropdown with unread count |

---

## EPIC 9 — Reviews & Ratings

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| REVIEW-001 | Review model & migrations | P2 | 🔲 | Salon reviews professional after collaboration |
| REVIEW-002 | Review API | P2 | 🔲 | POST/GET /reviews |
| REVIEW-003 | Review display in profiles | P2 | 🔲 | Star rating + comments in public profiles |

---

## EPIC 10 — Admin

| ID | Feature | Priority | Status | Notes |
|----|---------|----------|--------|-------|
| ADMIN-001 | Admin user model & role | P2 | 🔲 | Add "admin" role to UserRole enum |
| ADMIN-002 | Admin API (user management) | P2 | 🔲 | List, disable, verify users |
| ADMIN-003 | Admin dashboard (frontend) | P3 | 🔲 | Basic stats, user table, moderation tools |

---

## Implementation Order (by priority)

```
Phase 1 (Core — MVP):
  AUTH-002 → PROFILE-001 → PROFILE-002 → PROFILE-003 → PROFILE-004
  → SEARCH-001 → SEARCH-002 → SEARCH-003 → SEARCH-004
  → JOB-001 → JOB-002 → JOB-003 → JOB-004

Phase 2 (Engagement):
  JOB-005 → JOB-006 → JOB-007
  → MATCH-001 → MATCH-002 → MATCH-003 → MATCH-004
  → MSG-001 → MSG-002 → MSG-004
  → PROFILE-005 → PROFILE-006

Phase 3 (Growth):
  AUTH-003 → NOTIF-001..004 → REVIEW-001..003
  → SUB-001 → MSG-003 → MATCH-005

Phase 4 (Scale):
  SUB-002 → SUB-003 → AUTH-004 → ADMIN-001..003
```
