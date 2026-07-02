# Phase 2 — Complete Business Logic (Backend)

**Date:** 2026-07-02  
**Status:** Complete  
**Version:** 0.2.0 (Phase 2)

---

## Objectives

Replace mocked business logic with real engine implementations while continuing to use in-memory storage. Harden the prompt layer with structured parsing, validation, and injection protection.

---

## Completed Work

### Engines (`app/engines/`)
| Engine | Capabilities |
|--------|-------------|
| **JourneyEngine** | Profile-aware day planning, experience-level pacing, learning-style adaptation, rule-based fallback |
| **ProfileAnalysisEngine** | Strengths/focus areas from skills, experience, learning style, manager notes |
| **MentorEngine** | Task-type guidance, progress context, learning-style tips |
| **FAQEngine** | Knowledge base retrieval (6 entries), grounded answers, confidence scoring, fallback |
| **RegenerationEngine** | Profile snapshot diff detection, targeted task add/modify/remove |

### Prompt Layer (`app/services/prompt/`)
- **PromptBuilder** — system instructions + schema embedding per prompt type
- **OutputParser** — JSON extraction from markdown blocks, Pydantic schema validation
- **PromptService** — template loading, injection pattern detection (retained)

### LLM Output Schemas (`app/schemas/llm_outputs.py`)
- `JourneyGenerationOutput`, `ProfileAnalysisOutput`, `MentorGuidanceOutput`
- `FAQAnswerOutput`, `JourneyRegenerationOutput`

### Infrastructure
- **Profile snapshots** for change detection during regeneration
- **JourneyBuilder** utility extracted from services
- **FAQ knowledge base** (`app/data/faq_knowledge.json`)
- **Checklist toggle API** — `PATCH /journeys/{id}/tasks/{task_id}/checklist/{checklist_id}`
- Services refactored to use engines via `BaseLLMProvider` abstraction

---

## Files Created

- `app/engines/__init__.py`, `journey_engine.py`, `profile_engine.py`, `mentor_engine.py`, `faq_engine.py`, `regeneration_engine.py`
- `app/services/prompt/__init__.py`, `builder.py`, `parser.py`
- `app/schemas/llm_outputs.py`
- `app/models/profile_snapshot.py`
- `app/utils/journey_builder.py`
- `app/data/faq_knowledge.json`
- `tests/test_engines.py`

## Files Modified

- All 5 onboarding services (refactored to use engines)
- `app/core/dependencies.py` (engine DI wiring)
- `app/repositories/profile_repository.py` (snapshot storage)
- `app/routers/onboarding.py`, `controllers/onboarding_controller.py` (checklist endpoint)
- `app/schemas/journey.py` (ChecklistToggleRequest)
- `app/services/faq_service.py` (FAQSource mapping fix)

---

## APIs (unchanged + new)

| Method | Endpoint | Notes |
|--------|----------|-------|
| PATCH | `/api/v1/journeys/{id}/tasks/{task_id}/checklist/{checklist_id}` | **New** — toggle checklist item |

All 15 existing endpoints retained with enhanced business logic.

---

## Tests

- **38 tests passing** (29 Phase 1 + 9 engine unit tests)
- Engine tests: journey personalization, FAQ grounding/fallback, regeneration diff, output parsing, prompt builder

---

## Security Review

- Prompt injection detection in FAQ input and PromptBuilder system instructions
- FAQ grounding validation prevents high-confidence answers without sources
- Structured output validation prevents malformed LLM responses from reaching clients
- No authentication (deferred to Phase 3)

---

## Performance Notes

- Rule-based fallbacks avoid LLM latency when parsing fails
- Knowledge base retrieval is O(n) keyword scan — sufficient for 6 entries
- Engine singletons via `@lru_cache` in dependencies

---

## Decisions

1. **Engines + rule-based fallbacks** — ensures reliable demo even when mock LLM returns generic data
2. **Profile snapshots** stored in repository, captured before update
3. **Regeneration applies changes to Day 1 only** for added tasks (targeted, not all days)
4. **BaseLLMProvider** abstraction ready for OpenAI swap in Phase 3

---

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Rule-based fallbacks | Reliable output | Less "AI magic" in demo |
| In-memory snapshots | Simple change detection | Lost on restart |
| Keyword FAQ retrieval | Fast, no embeddings | Limited to known topics |
| Mock LLM retained | No API keys needed | Not production AI |

---

## Risks

1. Mock LLM still used — real OpenAI quality untested until Phase 3
2. FAQ knowledge base is static — needs expansion or RAG for production
3. Title-based journey comparison fragile for major restructures

---

## Pending Items (Phase 3)

- PostgreSQL persistence
- OpenAI integration
- Authentication & RBAC
- Alembic migrations
- Groq provider completion

---

## Next Phase Plan

1. PostgreSQL + SQLAlchemy repositories
2. OpenAI provider wiring with production prompts
3. JWT authentication and role-based authorization
4. Frontend API auth headers
5. E2E and integration tests
