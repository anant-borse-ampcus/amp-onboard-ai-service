# Phase 3 — Final Integration & Production Readiness (Backend)

**Date:** 2026-07-02
**Status:** Complete
**Version:** 0.3.0 (Phase 3)

---

## Objectives

Transform the service into a fully integrated, production-ready application:
persistent storage (PostgreSQL/SQLite via SQLAlchemy), database migrations,
real LLM execution (OpenAI/Groq) with graceful fallback, JWT authentication,
role-based authorization, and session handling — while keeping the app runnable
out of the box.

---

## Completed Work

### Persistent Storage (SQLAlchemy)
- Async SQLAlchemy 2.0 engine/session (`app/db/`)
- ORM models: `users`, `profiles`, `journeys` (nested journey structure stored as JSON)
- SQL repositories (`app/repositories/sql/`) implementing the same interface as the
  in-memory repositories, returning identical domain entities
- **Configurable storage backend** via `STORAGE_BACKEND=memory|database`
  - `memory` (default): zero-setup, runs anywhere, resets on restart
  - `database`: SQLAlchemy against `DATABASE_URL` (SQLite or PostgreSQL/asyncpg)
- Automatic table creation + demo data seeding on startup for the database backend

### Database Migrations (Alembic)
- `alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`
- Initial migration `0001_initial` (users, profiles, journeys with indexes)
- Sync migration URL via `ALEMBIC_DATABASE_URL`; runtime uses async engine

### LLM Integration
- **Groq provider** implemented (OpenAI-compatible API surface, `base_url` + timeout)
- **OpenAI provider** retained and wired through the factory
- **Mock provider** added to the factory (`LLM_PROVIDER=mock`) for offline/deterministic runs
- Engines resolve their provider via `LLMProviderFactory`; every engine has a
  rule-based fallback, so a provider error/timeout degrades gracefully instead of failing

### Authentication & Authorization
- `app/core/security.py`: PBKDF2-HMAC-SHA256 password hashing (stdlib) + JWT (PyJWT)
- Domain `User` + `UserRole` (manager | employee), auth DTOs
- `AuthService` (register/login/me) with user repositories (in-memory + SQL)
- `HTTPBearer` guards: `get_current_claims`, `require_roles(...)`
- Session handling via signed JWT access tokens (configurable expiry)
- Demo users seeded: `manager@example.com`, `alex.rivera@example.com` (password `password123`)

### Route Protection (RBAC)
- Manager-only: create/update/analyze profiles, generate/activate/regenerate journeys
- Authenticated (any role): read profiles/journeys, complete tasks/checklist, progress, mentor, FAQ, compare

### API / Infrastructure
- CORS configurable via `CORS_ORIGINS` (locked down outside development)
- Startup logs storage + LLM provider; DB bootstrap wrapped in error handling
- `ConflictError` / `AuthenticationError` / `AuthorizationError` mapped to proper HTTP codes

---

## Files Created

| Area | Files |
|------|-------|
| DB | `app/db/base.py`, `app/db/models.py`, `app/db/session.py`, `app/db/__init__.py` |
| SQL repos | `app/repositories/sql/{__init__,profile_repository,journey_repository,user_repository}.py` |
| User repo | `app/repositories/user_repository.py` |
| Auth | `app/core/security.py`, `app/models/user.py`, `app/schemas/auth.py`, `app/services/auth_service.py`, `app/controllers/auth_controller.py`, `app/routers/auth.py` |
| Migrations | `alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`, `migrations/versions/0001_initial.py` |
| Tests/scripts | `tests/test_auth.py`, `tests/test_sql_repositories.py`, `scripts/e2e_smoke.py` |

## Files Modified

- `app/config/settings.py`, `app/config/config_manager.py` (storage/auth/CORS/mock config)
- `app/llm/factory.py`, `app/llm/providers/groq_provider.py` (real Groq + mock)
- `app/core/dependencies.py` (backend selection, engine provider via factory, auth guards)
- `app/repositories/profile_repository.py`, `app/repositories/seed_data.py` (snapshots, demo users)
- `app/routers/__init__.py`, `app/routers/onboarding.py` (auth router + RBAC)
- `app/main.py` (lifespan DB bootstrap, CORS from settings)
- `requirements.txt`, `.env`, `.env.example`

---

## APIs Added

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/v1/auth/register` | public |
| POST | `/api/v1/auth/login` | public |
| GET | `/api/v1/auth/me` | bearer |

All Phase 1/2 onboarding endpoints now enforce authentication + role checks.

---

## Tests

- **51 backend tests passing** (health, core, engines, onboarding, auth, SQL repositories)
- New coverage: password hash/verify, JWT round-trip, login/register/me, protected-route 401,
  manager-only 403 for employees, SQL profile/journey/user CRUD (in-memory SQLite)
- `scripts/e2e_smoke.py`: 10-step end-to-end workflow (login → profile → analysis → journey →
  task completion → mentor → FAQ → regenerate → compare → RBAC) — all pass

---

## Security Review

- Passwords hashed with PBKDF2 (200k rounds) + per-user salt; constant-time verification
- JWT signed (HS256); expiry enforced; invalid/expired tokens rejected with 401
- Role-based authorization on every mutating onboarding route
- CORS restricted to configured origins outside development
- Prompt-injection detection retained in FAQ input path
- LLM output schema validation prevents malformed AI responses reaching clients
- Note: `JWT_SECRET` must be overridden in production (documented in `.env.example`)

---

## Performance Notes

- Async DB sessions, `pool_pre_ping`, connection pooling via SQLAlchemy
- API client retries (frontend) + engine fallbacks bound worst-case latency
- LLM timeout (`LLM_TIMEOUT_SECONDS`) prevents hung requests
- In-memory backend remains available for the fastest demo path

---

## Decisions

1. **Storage backend toggle** so the app runs with zero external services by default,
   while offering full PostgreSQL support for production.
2. **Journey stored as JSON** column — matches the document-shaped domain and keeps
   migrations simple without sacrificing queryability by profile/status.
3. **Groq via OpenAI-compatible client** — avoids an extra SDK dependency.
4. **PBKDF2 over bcrypt** — pure stdlib, no native build dependencies on Windows.
5. **Engines depend on `BaseLLMProvider` via factory** — provider is now a config switch.

---

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Default `memory` + `mock` | Runs anywhere instantly | Must opt into DB/LLM for "real" mode |
| JSON journey column | Simple schema/migrations | No relational queries into tasks |
| Stateless JWT (no refresh) | Simple session model | No server-side revocation before expiry |

---

## Risks

1. Provided Groq key may be invalid/expired → engines fall back to rule-based output
2. No token refresh/blocklist (acceptable for hackathon scope)
3. JSON columns limit deep task-level SQL querying

---

## Pending / Future

- Refresh tokens + revocation list
- Per-task relational schema if analytics require it
- Rate limiting and audit logging
- Postgres-specific integration tests in CI

---

## How to Run

```bash
# In-memory + mock (default, zero setup)
uvicorn app.main:app --reload

# Database backend (SQLite)
#   set STORAGE_BACKEND=database in .env, then:
python -m alembic upgrade head   # optional; app also auto-creates tables
uvicorn app.main:app --reload

# Real LLM: set LLM_PROVIDER=groq (or openai) and the matching API key in .env
```
