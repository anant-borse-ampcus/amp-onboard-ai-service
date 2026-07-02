"""Unit tests for Phase 2 business logic engines."""

import pytest

from app.engines.faq_engine import FAQEngine
from app.engines.journey_engine import JourneyEngine
from app.engines.profile_engine import ProfileAnalysisEngine
from app.engines.regeneration_engine import RegenerationEngine
from app.llm.providers.mock_provider import MockLLMProvider
from app.models.journey import Journey, JourneyDay, JourneyStatus, JourneyTask, TaskType
from app.models.profile import EmployeeProfile, ExperienceLevel, LearningStyle
from app.models.profile_snapshot import ProfileSnapshot
from app.repositories.seed_data import get_demo_journey, get_demo_profile
from app.services.prompt import OutputParser, PromptBuilder
from app.services.prompt_service import PromptService


@pytest.fixture
def journey_engine() -> JourneyEngine:
    ps = PromptService()
    return JourneyEngine(PromptBuilder(ps), OutputParser(), MockLLMProvider())


@pytest.fixture
def profile_engine() -> ProfileAnalysisEngine:
    ps = PromptService()
    return ProfileAnalysisEngine(PromptBuilder(ps), OutputParser(), MockLLMProvider())


@pytest.fixture
def faq_engine() -> FAQEngine:
    ps = PromptService()
    return FAQEngine(PromptBuilder(ps), OutputParser(), MockLLMProvider())


@pytest.fixture
def regeneration_engine() -> RegenerationEngine:
    ps = PromptService()
    return RegenerationEngine(PromptBuilder(ps), OutputParser(), MockLLMProvider())


@pytest.fixture
def demo_profile() -> EmployeeProfile:
    return get_demo_profile()


@pytest.mark.asyncio
async def test_journey_engine_generates_personalized_days(
    journey_engine: JourneyEngine, demo_profile: EmployeeProfile
) -> None:
    output = await journey_engine.generate(demo_profile, total_days=5)
    assert len(output.days) == 5
    assert output.summary
    rule_based = journey_engine._generate_rule_based(demo_profile, 5)
    assert demo_profile.team in rule_based.days[0].tasks[-1].title


def test_journey_engine_adjusts_for_experience(
    journey_engine: JourneyEngine,
) -> None:
    junior = get_demo_profile().model_copy(update={"experience_level": ExperienceLevel.JUNIOR})
    senior = get_demo_profile().model_copy(update={"experience_level": ExperienceLevel.SENIOR})
    junior_out = journey_engine._generate_rule_based(junior, 3)
    senior_out = journey_engine._generate_rule_based(senior, 3)
    junior_tasks = sum(len(d.tasks) for d in junior_out.days)
    senior_tasks = sum(len(d.tasks) for d in senior_out.days)
    assert junior_tasks >= senior_tasks


@pytest.mark.asyncio
async def test_profile_analysis_engine(
    profile_engine: ProfileAnalysisEngine, demo_profile: EmployeeProfile
) -> None:
    output = await profile_engine.analyze(demo_profile)
    assert len(output.strengths) > 0
    assert len(output.focus_areas) > 0
    assert "mid" in output.recommended_pace.lower() or "5" in output.recommended_pace


@pytest.mark.asyncio
async def test_faq_engine_grounded_answer(faq_engine: FAQEngine) -> None:
    output = await faq_engine.answer("How do I set up VPN access?")
    assert output.fallback is False
    assert output.confidence > 0.5
    assert len(output.sources) > 0


@pytest.mark.asyncio
async def test_faq_engine_fallback(faq_engine: FAQEngine) -> None:
    output = await faq_engine.answer("What is the meaning of life?")
    assert output.fallback is True
    assert output.confidence < 0.5


def test_regeneration_detects_team_change(regeneration_engine: RegenerationEngine) -> None:
    profile = get_demo_profile()
    snapshot = ProfileSnapshot.from_profile(profile)
    updated = profile.model_copy(update={"team": "Data Engineering"})
    diff = regeneration_engine.detect_changes(snapshot, updated)
    assert diff.team_changed is True
    assert "team" in diff.changed_fields


@pytest.mark.asyncio
async def test_regeneration_rule_based_changes(
    regeneration_engine: RegenerationEngine,
) -> None:
    profile = get_demo_profile().model_copy(update={"team": "Data Engineering"})
    journey = get_demo_journey()
    snapshot = ProfileSnapshot.from_profile(get_demo_profile())
    diff = regeneration_engine.detect_changes(snapshot, profile)
    changes = await regeneration_engine.regenerate(profile, journey, diff)
    assert len(changes.added) > 0
    assert changes.summary


def test_output_parser_extracts_json() -> None:
    parser = OutputParser()
    content = 'Here is the result:\n```json\n{"summary": "test", "days": []}\n```'
    data = parser.parse_json(content)
    assert data["summary"] == "test"


def test_prompt_builder_includes_schema() -> None:
    builder = PromptBuilder(PromptService())
    system, user = builder.build("journey_generation", {"name": "Test", "role": "Dev", "team": "Eng", "experience_level": "mid", "skills": "Python", "learning_style": "hands_on", "start_date": "2026-01-01", "total_days": "5"})
    assert "JSON" in system
    assert "days" in user
