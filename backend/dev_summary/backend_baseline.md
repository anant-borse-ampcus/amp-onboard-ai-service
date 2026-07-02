# Backend Baseline — Stage 1 Summary

**Project:** AMP Onboard AI Service  
**Stage:** 1 — Backend Foundation (Baseline)  
**Version:** 0.1.0  
**Date:** 2026-07-02  
**Status:** Complete

---

## Architecture

The backend follows an **MVC-inspired layered architecture** on top of FastAPI:

```
Request → Router → Controller → Service → Repository / LLM Provider
                ↓
            Schema (DTO)
                ↓
            Model (Domain Entity)
```

### Layers

| Layer | Responsibility | Location |
|-------|---------------|----------|
| **Router** | HTTP routing, OpenAPI metadata, dependency injection wiring | `app/routers/` |
| **Controller** | Request orchestration, thin delegation to services | `app/controllers/` |
| **Service** | Business logic, cross-cutting orchestration | `app/services/` |
| **Repository** | Data access abstraction (interface + implementations) | `app/repositories/` |
| **Model** | Domain entities with identity and timestamps | `app/models/` |
| **Schema** | Request/response DTOs (Pydantic) | `app/schemas/` |
| **LLM** | Provider abstraction for AI generation | `app/llm/` |
| **Core** | Logging, exceptions, error handlers, DI | `app/core/` |
| **Config** | Settings and configuration manager | `app/config/` |
| **Middleware** | Cross-cutting HTTP concerns | `app/middleware/` |
| **Utils** | Shared helpers | `app/utils/` |

### Key Design Decisions

1. **Application factory pattern** — `create_app()` in `app/main.py` enables testability and clean lifespan management.
2. **Dependency injection via FastAPI `Depends()`** — Centralized in `app/core/dependencies.py` with `@lru_cache` for singletons (repository, LLM factory).
3. **Repository pattern** — `BaseRepository[T]` abstract interface with `MockInMemoryRepository` for baseline development.
4. **LLM provider abstraction** — `BaseLLMProvider` with factory pattern; OpenAI fully structured, Groq as intentional placeholder.
5. **Standardized error envelope** — All errors return `ErrorResponse` with `code`, `message`, and optional `details`.
6. **Configuration via Pydantic Settings** — Environment variables loaded from `.env` with typed validation.
7. **ConfigManager singleton** — Wraps settings for runtime access and LLM config resolution.

### Request Flow (Health Endpoint)

```
GET /health
  → health.router
  → HealthController.get_health()
  → HealthService.check_health()
  → MockInMemoryRepository.ping()
  → HealthResponse
```

---

## Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app factory & entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Pydantic Settings (env loading)
│   │   └── config_manager.py        # Runtime configuration manager
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logging.py               # Logging setup & helpers
│   │   ├── exceptions.py            # Custom exception hierarchy
│   │   ├── error_handlers.py        # Global exception handlers
│   │   └── dependencies.py          # FastAPI DI providers
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── request_logging.py       # Request/response logging middleware
│   ├── routers/
│   │   ├── __init__.py              # api_router aggregation
│   │   └── health.py                # Health check routes
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── health_controller.py     # Health MVC controller
│   ├── services/
│   │   ├── __init__.py
│   │   └── health_service.py        # Health business logic
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract BaseRepository[T]
│   │   └── mock_in_memory.py        # In-memory mock implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py                  # BaseEntity, TimestampMixin
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py                # ErrorResponse, MessageResponse
│   │   └── health.py                # HealthResponse
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                  # BaseLLMProvider, LLMRequest/Response
│   │   ├── factory.py               # LLMProviderFactory
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── openai_provider.py   # OpenAI implementation
│   │       └── groq_provider.py       # Groq placeholder
│   └── utils/
│       ├── __init__.py
│       └── helpers.py               # Shared utilities
├── prompts/
│   └── .gitkeep                     # Prompt templates (Phase 1)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures (async client)
│   └── test_health.py               # Health & OpenAPI tests
├── dev_summary/
│   └── backend_baseline.md          # This document
├── requirements.txt
├── pyproject.toml
├── .env.example
└── .env
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | ≥0.115.0 | Web framework |
| `uvicorn[standard]` | ≥0.32.0 | ASGI server |
| `pydantic` | ≥2.9.0 | Data validation & schemas |
| `pydantic-settings` | ≥2.6.0 | Environment configuration |
| `python-dotenv` | ≥1.0.1 | `.env` file loading |
| `httpx` | ≥0.27.0 | Async HTTP client (testing) |
| `openai` | ≥1.54.0 | OpenAI SDK |
| `pytest` | ≥8.3.0 | Test framework |
| `pytest-asyncio` | ≥0.24.0 | Async test support |

### Install & Run

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env    # configure as needed
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Verified Endpoints

| Endpoint | Status | Description |
|----------|--------|-------------|
| `GET /health` | 200 OK | Service health check |
| `GET /docs` | 200 OK | Swagger UI |
| `GET /redoc` | 200 OK | ReDoc documentation |
| `GET /openapi.json` | 200 OK | OpenAPI 3.x schema |

### Health Response (verified)

```json
{
  "status": "healthy",
  "service": "AMP Onboard AI Service",
  "version": "0.1.0",
  "environment": "development",
  "repository": "connected"
}
```

---

## Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI over Flask/Django | Native async, automatic OpenAPI, Pydantic integration |
| MVC with separate controllers | Clear separation; routers stay thin |
| Pydantic Settings for config | Type-safe env loading, validation, `.env` support |
| `@lru_cache` singletons for DI | Simple DI without heavy framework; sufficient for baseline |
| Mock in-memory repository | No database dependency in Stage 1; swappable later |
| LLM factory + provider interface | Supports multi-provider switching via `LLM_PROVIDER` env var |
| Groq as placeholder | Interface defined; implementation deferred to Development Phase 1 |
| Standardized `ErrorResponse` envelope | Consistent API error contract across all endpoints |
| Request logging middleware | `X-Request-ID` and `X-Process-Time-Ms` headers on all responses |
| CORS open in development | Restricted to empty origins in production |
| No auth in baseline | Explicitly out of scope for Stage 1 |
| No onboarding APIs | Explicitly out of scope for Stage 1 |
| Prompts folder empty | Reserved for Development Phase 1 prompt templates |

---

## Pending Work

The following items are **intentionally deferred** to Development Phase 1 and beyond:

### Development Phase 1
- [ ] Onboarding API endpoints (CRUD, workflow)
- [ ] AI content generation service using LLM abstraction
- [ ] Groq provider full implementation
- [ ] Prompt templates in `prompts/` folder
- [ ] Real database repository (PostgreSQL/SQLite)
- [ ] Database migrations (Alembic)
- [ ] Domain-specific models and schemas

### Future Phases
- [ ] Authentication & authorization (JWT/OAuth)
- [ ] Rate limiting middleware
- [ ] Caching layer (Redis)
- [ ] Background task processing (Celery/ARQ)
- [ ] Observability (metrics, tracing)
- [ ] CI/CD pipeline configuration
- [ ] Docker containerization
- [ ] API versioning strategy
- [ ] Integration tests with real LLM providers

---

## Instructions for Development Stage

### Getting Started

1. **Activate the backend environment** and install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment** — copy `.env.example` to `.env` and set:
   - `OPENAI_API_KEY` when testing OpenAI generation
   - `LLM_PROVIDER` to switch between `openai` and `groq`

3. **Run the server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### Adding a New Feature (Follow the Pattern)

1. **Model** — Define domain entity in `app/models/`
2. **Schema** — Create request/response DTOs in `app/schemas/`
3. **Repository** — Extend `BaseRepository[T]` or add methods to a new repository in `app/repositories/`
4. **Service** — Implement business logic in `app/services/`
5. **Controller** — Add thin controller in `app/controllers/`
6. **Router** — Wire routes with `Depends()` in `app/routers/`, register in `api_router`
7. **Dependencies** — Register new DI providers in `app/core/dependencies.py`
8. **Tests** — Add tests in `tests/`

### LLM Integration Guide

```python
from app.core.dependencies import get_llm_provider
from app.llm.base import LLMRequest, LLMMessage

provider = get_llm_provider()
request = LLMRequest(
    messages=[
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="Hello"),
    ],
)
response = await provider.generate(request)
```

Or via factory:
```python
from app.llm.factory import LLMProviderFactory
from app.config.config_manager import get_config_manager

factory = LLMProviderFactory(get_config_manager())
response = await factory.generate(request)
```

### Coding Standards

- **Python 3.11+** with full type hints
- **Async-first** — use `async def` for I/O-bound operations
- **Pydantic v2** for all schemas and settings
- **No business logic in routers** — delegate to controllers/services
- **No direct DB/LLM calls from controllers** — go through service layer
- **Custom exceptions** — raise `AppException` subclasses; never return raw errors
- **Logging** — use `get_logger(__name__)` from `app.core.logging`
- **Line length** — 100 characters (ruff config in `pyproject.toml`)
- **Imports** — absolute imports from `app.*`

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | AMP Onboard AI Service | Display name |
| `APP_VERSION` | 0.1.0 | Semantic version |
| `APP_ENV` | development | `development` \| `staging` \| `production` |
| `DEBUG` | false | Debug mode |
| `HOST` | 0.0.0.0 | Bind host |
| `PORT` | 8000 | Bind port |
| `LOG_LEVEL` | INFO | Logging level |
| `LLM_PROVIDER` | openai | Active LLM provider |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | gpt-4o-mini | Default OpenAI model |
| `GROQ_API_KEY` | — | Groq API key |
| `GROQ_MODEL` | llama-3.3-70b-versatile | Default Groq model |

---

## Verification Checklist

- [x] FastAPI application initializes
- [x] MVC architecture in place
- [x] Configuration & environment loading
- [x] Logging configured
- [x] Error handling & exception handlers
- [x] Dependency injection
- [x] Repository pattern with mock implementation
- [x] Service pattern
- [x] LLM abstraction with OpenAI + Groq placeholder
- [x] Configuration manager
- [x] Middleware structure
- [x] Router structure
- [x] Schema & model structure
- [x] Testing structure (2 tests passing)
- [x] Utilities & prompts folder
- [x] Health endpoint operational
- [x] Swagger UI accessible at `/docs`
- [x] Application runs successfully

**Stage 1 (Backend Baseline) is complete. Development Phase 1 may proceed.**
