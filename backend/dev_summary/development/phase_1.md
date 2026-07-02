# Phase 1 — Foundation (Backend)

**Date:** 2026-07-02  
**Status:** Complete  
**Version:** 0.1.0 (Phase 1)

---

## Objectives

Build the complete application foundation using mocked data and in-memory storage. Demonstrate the full onboarding business workflow via mock API endpoints without PostgreSQL, authentication, or real OpenAI integration.

---

## Completed Work

### Architecture & Infrastructure
- Extended MVC layered architecture (Router → Controller → Service → Repository)
- Domain models for profiles, journeys, mentor guidance, FAQ, and regeneration
- Request/Response DTOs with Pydantic validation
- In-memory repositories with seed data
- Prompt service architecture with template loading, rendering, and injection protection
- Mock LLM provider returning structured JSON responses
- AI prompt templates (5 templates in `prompts/`)
- Global exception handling including new `ConflictError`
- Dependency injection for all onboarding services

### Business Workflow (Mock)
- Profile CRUD with email uniqueness validation
- AI profile analysis (mock)
- Journey generation with day-wise task planning
- Journey activation and versioning
- Task completion tracking
- Progress calculation
- AI mentor guidance per task
- Grounded FAQ with fallback responses
- Journey regeneration and comparison

### APIs Implemented
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/profiles` | Create employee profile |
| GET | `/api/v1/profiles` | List all profiles |
| GET | `/api/v1/profiles/{id}` | Get profile by ID |
| PUT | `/api/v1/profiles/{id}` | Update profile |
| POST | `/api/v1/profiles/{id}/analyze` | AI profile analysis |
| POST | `/api/v1/journeys/generate` | Generate onboarding journey |
| GET | `/api/v1/journeys/{id}` | Get journey by ID |
| GET | `/api/v1/journeys/profile/{id}` | List journeys for profile |
| POST | `/api/v1/journeys/{id}/activate` | Activate journey |
| PATCH | `/api/v1/journeys/{id}/tasks/{task_id}` | Complete/uncomplete task |
| GET | `/api/v1/progress/profile/{id}` | Get onboarding progress |
| POST | `/api/v1/mentor/guidance` | Get AI mentor guidance |
| POST | `/api/v1/faq/ask` | Ask FAQ question |
| POST | `/api/v1/journeys/regenerate` | Regenerate journey |
| GET | `/api/v1/journeys/compare/{prev}/{curr}` | Compare journeys |

---

## Files Created

### Models
- `app/models/profile.py`
- `app/models/journey.py`
- `app/models/mentor.py`
- `app/models/faq.py`
- `app/models/regeneration.py`

### Schemas
- `app/schemas/profile.py`
- `app/schemas/journey.py`
- `app/schemas/mentor.py`
- `app/schemas/faq.py`
- `app/schemas/regeneration.py`

### Repositories
- `app/repositories/profile_repository.py`
- `app/repositories/journey_repository.py`
- `app/repositories/seed_data.py`

### Services
- `app/services/profile_service.py`
- `app/services/journey_service.py`
- `app/services/mentor_service.py`
- `app/services/faq_service.py`
- `app/services/regeneration_service.py`
- `app/services/prompt_service.py`

### LLM
- `app/llm/providers/mock_provider.py`

### Controllers & Routers
- `app/controllers/onboarding_controller.py`
- `app/routers/onboarding.py`

### Utilities
- `app/utils/mappers.py`

### Prompts
- `prompts/journey_generation.txt`
- `prompts/mentor_guidance.txt`
- `prompts/faq_answer.txt`
- `prompts/profile_analysis.txt`
- `prompts/journey_regeneration.txt`

### Tests
- `tests/test_onboarding.py`

---

## Files Modified

- `app/models/__init__.py`
- `app/schemas/__init__.py`
- `app/core/exceptions.py` — added `ConflictError`
- `app/core/dependencies.py` — onboarding DI wiring
- `app/routers/__init__.py` — registered onboarding router
- `requirements.txt` — `pydantic[email]`

---

## Tests

- **29 tests passing** (19 baseline + 10 onboarding)
- Coverage: profile CRUD, journey generation, mentor, FAQ, progress, fallback responses

---

## Security Review

- Prompt injection pattern detection in `PromptService.validate_input()`
- Input length limits on FAQ questions (max 2000 chars)
- Structured JSON output validation for LLM responses
- No authentication (deferred to Phase 3)
- CORS open in development mode only

---

## Performance Notes

- In-memory storage — no database latency
- Mock LLM responses — sub-millisecond generation
- `@lru_cache` singleton repositories for request lifecycle
- Seed data pre-loaded on first repository access

---

## Decisions

1. **Mock LLM over OpenAI** — Phase 1 uses deterministic structured responses for reliable demos
2. **Separate profile/journey repositories** — cleaner domain separation vs generic mock repo
3. **Prompt templates as `.txt` files** — simple, versionable, no template engine dependency
4. **API prefix `/api/v1`** — prepares for Phase 3 frontend integration
5. **Seed demo data** — enables immediate end-to-end demonstration

---

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Mock LLM | Deterministic, fast, no API keys | Not production-quality AI |
| In-memory repos | Simple, fast | Data lost on restart |
| No auth | Faster Phase 1 delivery | Must add in Phase 3 |
| Prompt injection regex | Lightweight protection | Not comprehensive security |

---

## Risks

1. Mock LLM responses may not reflect real AI quality — mitigated in Phase 2/3
2. In-memory data loss on server restart — acceptable for Phase 1
3. Frontend not yet connected to backend APIs — Phase 2 will bridge
4. Groq provider still placeholder — not needed until Phase 3

---

## Pending Items

- Real business logic engines (Phase 2)
- Frontend API integration (Phase 2)
- PostgreSQL persistence (Phase 3)
- OpenAI integration (Phase 3)
- Authentication & RBAC (Phase 3)

---

## Next Phase Plan (Phase 2)

1. Replace mock business logic with real journey/mentor/FAQ engines
2. Implement prompt builder, output validation, structured parsing
3. Connect frontend mock services to backend APIs
4. Add unit tests for business logic engines
5. Freeze request/response models for API contract
