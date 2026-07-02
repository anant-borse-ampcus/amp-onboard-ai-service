# AMP Onboard AI Service

FastAPI backend for **AMP Onboard AI** — an AI-assisted employee onboarding platform. The service handles authentication, role-based access, onboarding journeys, mentor/FAQ assistance, and system administration.

Companion frontend: [amp-onboard-ai-web](../amp-onboard-ai-web)

## Hackathon Problem Solved

**Problem 4 — New-Hire Onboarding Companion** (Advanced)

### Problem Statement

> Onboarding is inconsistent and overwhelming. Build a companion that generates a personalized first-week plan from a few inputs (role, team, start date, a short skills note) and answers a new hire's common questions from a provided FAQ set. It should produce a day-by-day checklist and adapt the plan when the user changes an input. The strongest solutions feel genuinely personal and reduce a manager's setup work to near-zero. Non-engineers own the onboarding content, tone, and demo story; engineers handle the generation logic, state, and interface. Judged on personalization quality and how complete the experience feels.

**Acceptance Criteria**

- Collects a few profile inputs and generates a structured first-week plan.
- Regenerates or adjusts the plan when inputs change.
- Answers common new-hire questions from a provided FAQ/content set.
- Presents the plan as a clear, day-by-day checklist in a live demo.

**Constraints**

- Must use an AI/LLM call to generate or personalize the plan.
- Plan content must visibly change in response to at least two different profiles.

**Out of Scope**

- No HRIS or single-sign-on integration.
- No email/Slack provisioning — generation and display only.
- No long-term storage of new-hire data.

### How This Backend Addresses Problem 4

| Requirement | Implementation |
|-------------|----------------|
| Profile inputs → first-week plan | `POST /api/v1/profiles` + `POST /api/v1/journeys/generate` via the journey engine (LLM-backed) |
| Regenerate on input change | `PUT /api/v1/profiles/{id}` + `POST /api/v1/journeys/regenerate` with side-by-side comparison |
| FAQ from provided content set | `POST /api/v1/faq/ask` grounded on admin-managed knowledge base (`/api/v1/admin/knowledge`) |
| Day-by-day checklist | Journey model stores days, tasks, and checklist items; exposed via journey/progress APIs |
| LLM personalization | Pluggable providers (`mock`, `openai`, `groq`) in profile analysis, journey generation, mentor, and FAQ engines |
| Different plans per profile | Profile fields (role, team, skills, experience, learning style) drive distinct LLM prompts |

## Features

- **JWT authentication** with role-based authorization (`system_admin`, `manager`, `employee`)
- **Onboarding workflows** — employee profiles, AI journey generation, task/checklist tracking, progress, regeneration, and comparison
- **AI engines** — profile analysis, journey generation, mentor guidance, and grounded FAQ (with rule-based fallbacks when the LLM is unavailable)
- **System admin APIs** — organization branding, AI config, templates, departments, resources, knowledge base, and analytics
- **Pluggable LLM providers** — `mock` (default, offline), `openai`, or `groq`
- **In-memory storage by default** — runs with zero external services; SQLAlchemy/Alembic infrastructure is included for persistent storage

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2
- SQLAlchemy 2.0 (async) + Alembic migrations
- PyJWT + PBKDF2 password hashing

## Setup Instructions

### 1. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install "sqlalchemy[asyncio]" alembic pyjwt aiosqlite
```

### 3. Configure environment

```bash
cp .env.example .env
```

Key variables (see `.env.example` for the full list):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | `development`, `staging`, or `production` |
| `PORT` | `8000` | Server port |
| `LLM_PROVIDER` | `mock` | `mock`, `openai`, or `groq` |
| `OPENAI_API_KEY` | — | Required when `LLM_PROVIDER=openai` |
| `GROQ_API_KEY` | — | Required when `LLM_PROVIDER=groq` |
| `JWT_SECRET` | dev placeholder | **Override in production** (32+ chars) |

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Demo Accounts

Seeded on startup (password for all: `password123`):

| Role | Email |
|------|-------|
| System Admin | `admin@example.com` |
| Manager | `manager@example.com` |
| Employee | `alex.rivera@example.com` |

## API Overview

### Health

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/health` | Public |

### Authentication

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/v1/auth/register` | Public |
| POST | `/api/v1/auth/login` | Public |
| GET | `/api/v1/auth/me` | Bearer |

### Onboarding

| Method | Endpoint | Auth |
|--------|----------|------|
| POST/GET/PUT | `/api/v1/profiles` | Manager (write), Authenticated (read) |
| POST | `/api/v1/profiles/{id}/analyze` | Manager |
| POST | `/api/v1/journeys/generate` | Manager |
| GET | `/api/v1/journeys/{id}` | Authenticated |
| POST | `/api/v1/journeys/{id}/activate` | Manager |
| PATCH | `/api/v1/journeys/{id}/tasks/{task_id}` | Authenticated |
| GET | `/api/v1/progress/profile/{profile_id}` | Authenticated |
| POST | `/api/v1/mentor/guidance` | Authenticated |
| POST | `/api/v1/faq/ask` | Authenticated |
| POST | `/api/v1/journeys/regenerate` | Manager |
| GET | `/api/v1/journeys/compare/{prev}/{current}` | Authenticated |

### Branding (public)

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/v1/branding` | Public |

### System Admin (`/api/v1/admin/*`)

All endpoints require the `system_admin` role. Covers organization, AI config, templates, departments, resources, knowledge base, and analytics.

## LLM Providers

Set `LLM_PROVIDER` in `.env`:

- **`mock`** — Deterministic offline responses; ideal for development and tests
- **`openai`** — Set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` (default `gpt-4o-mini`)
- **`groq`** — Set `GROQ_API_KEY` and optionally `GROQ_MODEL` (default `llama-3.3-70b-versatile`)

All AI engines degrade gracefully to rule-based output if the provider fails or times out.

## Database Migrations

Alembic is configured for SQLite by default (`sqlite:///./amp_onboard.db`). The app currently uses in-memory repositories at runtime; SQL models and migrations are available for persistent storage.

```bash
# Apply migrations
python -m alembic upgrade head

# Create a new migration (after model changes)
python -m alembic revision --autogenerate -m "description"
```

## Testing

```bash
# Run all tests
python -m pytest

# Verbose output
python -m pytest -v
```

**59 tests** cover health, auth, onboarding, admin, engines, and SQL repositories.

### End-to-end smoke test

Runs a full workflow (login → profile → journey → tasks → mentor → FAQ → regenerate → compare) using the mock LLM and in-memory storage:

```bash
python scripts/e2e_smoke.py
```

## Project Structure

```
amp-onboard-ai-service/
├── app/
│   ├── config/          # Settings and config manager
│   ├── controllers/     # HTTP request handlers
│   ├── core/            # Security, dependencies, exceptions
│   ├── db/              # SQLAlchemy models and session
│   ├── engines/         # AI engines (profile, journey, mentor, FAQ)
│   ├── llm/             # LLM provider abstraction
│   ├── middleware/      # Request logging
│   ├── models/          # Domain models
│   ├── repositories/    # Data access (in-memory + SQL)
│   ├── routers/         # FastAPI route definitions
│   ├── schemas/         # Pydantic request/response DTOs
│   ├── services/        # Business logic
│   └── main.py          # Application entry point
├── migrations/          # Alembic migration scripts
├── scripts/             # Utility scripts (e2e smoke test)
├── tests/               # Pytest test suite
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

## Development Notes

- CORS allows all origins in `development`; restrict origins in staging/production.
- Override `JWT_SECRET` before deploying to any shared environment.
- Development summaries and phase notes live under `backend/dev_summary/`.

## License

Internal — Ampcus Tech Pvt Ltd (Hackathon project).
