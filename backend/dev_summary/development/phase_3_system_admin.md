# Phase 3 Addendum — System Admin Role (Backend)

**Date:** 2026-07-02
**Status:** Complete
**Version:** 0.3.1

---

## Objective

Introduce a third role, **System Admin** (Super Admin), alongside Manager and
Employee, with capabilities for organization configuration, AI management,
knowledge base, templates, departments, company resources, and analytics.

## Roles & Capabilities

| Role | Capabilities |
|------|--------------|
| **System Admin** | Configure Organization, Manage AI, Manage Knowledge Base, Manage Templates, View Analytics, Manage Departments, Publish Onboarding Content, Company Resources, Branding, Settings |
| **Manager** | Create Employee, Generate Plan, Review Plan, Regenerate Plan, Track Employee Progress |
| **Employee** | View Dashboard, Complete Tasks, Ask AI Mentor, Ask FAQ, Track Progress |

## Completed Work

- Added `UserRole.SYSTEM_ADMIN` and seeded demo admin `admin@example.com` / `password123`
- New admin domain (`app/models/admin.py`): `OrganizationConfig`, `AIConfig`,
  `OnboardingTemplate`, `Department`, `CompanyResource`, `KnowledgeEntry`
- Admin DTOs (`app/schemas/admin.py`)
- `AdminRepository` (in-memory, seeded) + `KnowledgeRepository` (seeded from `faq_knowledge.json`)
- `AdminService` incl. analytics computed from profiles/journeys
- `AdminController` + `app/routers/admin.py` — all endpoints guarded by `require_roles("system_admin")`
- **Knowledge base is now shared with the FAQ engine**: admin edits immediately affect grounded FAQ answers
- DI wiring for admin singletons

## Admin API (all `system_admin` only)

| Method | Endpoint |
|--------|----------|
| GET/PUT | `/api/v1/admin/organization` |
| GET/PUT | `/api/v1/admin/ai-config` |
| GET/POST | `/api/v1/admin/templates` |
| PUT/DELETE | `/api/v1/admin/templates/{id}` |
| POST | `/api/v1/admin/templates/{id}/publish` |
| GET/POST | `/api/v1/admin/departments`, DELETE `/{id}` |
| GET/POST | `/api/v1/admin/resources`, DELETE `/{id}` |
| GET/POST | `/api/v1/admin/knowledge`, DELETE `/{id}` |
| GET | `/api/v1/admin/analytics` |

## Tests

- **59 backend tests passing** (added `tests/test_admin.py`: admin login, RBAC 403 for
  managers, analytics, org update, templates CRUD + publish, AI config, departments/resources,
  and KB-reflects-in-FAQ integration)

## Files Created

`app/models/admin.py`, `app/schemas/admin.py`, `app/repositories/admin_repository.py`,
`app/services/admin_service.py`, `app/controllers/admin_controller.py`,
`app/routers/admin.py`, `tests/test_admin.py`

## Files Modified

`app/models/user.py` (role), `app/repositories/seed_data.py` (admin user),
`app/engines/faq_engine.py` (shared knowledge repository),
`app/core/dependencies.py` (admin DI + KB wiring), `app/routers/__init__.py`

## Notes / Trade-offs

- Admin content uses in-memory storage (consistent with the current default backend);
  can be migrated to SQLAlchemy following the existing repository pattern.
- Analytics are computed on-read from the profile/journey repositories.
