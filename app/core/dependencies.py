from functools import lru_cache
from typing import Any, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.config_manager import ConfigManager, get_config_manager
from app.config.settings import Settings, get_settings
from app.controllers.admin_controller import AdminController
from app.controllers.auth_controller import AuthController
from app.controllers.onboarding_controller import (
    FAQController,
    JourneyController,
    MentorController,
    ProfileController,
    RegenerationController,
)
from app.controllers.health_controller import HealthController
from app.core.security import (
    AuthenticationError,
    AuthorizationError,
    decode_access_token,
    hash_password,
)
from app.engines.faq_engine import FAQEngine
from app.engines.journey_engine import JourneyEngine
from app.engines.mentor_engine import MentorEngine
from app.engines.profile_engine import ProfileAnalysisEngine
from app.engines.regeneration_engine import RegenerationEngine
from app.llm.base import BaseLLMProvider
from app.llm.factory import LLMProviderFactory
from app.repositories.admin_repository import AdminRepository, KnowledgeRepository
from app.repositories.base import BaseRepository
from app.repositories.journey_repository import JourneyRepository
from app.repositories.mock_in_memory import MockInMemoryRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.seed_data import get_demo_journey, get_demo_profile, get_demo_users
from app.repositories.user_repository import InMemoryUserRepository
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.faq_service import FAQService
from app.services.health_service import HealthService
from app.services.journey_service import JourneyService
from app.services.mentor_service import MentorService
from app.services.profile_service import ProfileService
from app.services.prompt import OutputParser, PromptBuilder
from app.services.prompt_service import PromptService
from app.services.regeneration_service import RegenerationService
from app.utils.journey_builder import JourneyBuilder

_bearer = HTTPBearer(auto_error=False)


def get_settings_dependency() -> Settings:
    return get_settings()


def get_config_manager_dependency() -> ConfigManager:
    return get_config_manager()


@lru_cache
def _get_mock_repository() -> MockInMemoryRepository:
    return MockInMemoryRepository()


def get_repository() -> BaseRepository:
    return _get_mock_repository()


@lru_cache
def _get_llm_factory() -> LLMProviderFactory:
    return LLMProviderFactory(get_config_manager())


def get_llm_provider() -> BaseLLMProvider:
    return _get_llm_factory().create()


def get_health_service(
    config_manager: ConfigManager = Depends(get_config_manager_dependency),
    repository: BaseRepository = Depends(get_repository),
) -> HealthService:
    return HealthService(config_manager=config_manager, repository=repository)


def _get_health_controller(
    health_service: HealthService = Depends(get_health_service),
) -> HealthController:
    return HealthController(health_service=health_service)


@lru_cache
def _get_user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@lru_cache
def _get_profile_repository() -> ProfileRepository:
    return ProfileRepository()


@lru_cache
def _get_journey_repository() -> JourneyRepository:
    return JourneyRepository()


@lru_cache
def _get_admin_repository() -> AdminRepository:
    return AdminRepository()


@lru_cache
def _get_knowledge_repository() -> KnowledgeRepository:
    return KnowledgeRepository()


@lru_cache
def _get_prompt_service() -> PromptService:
    return PromptService()


@lru_cache
def _get_prompt_builder() -> PromptBuilder:
    return PromptBuilder(_get_prompt_service())


@lru_cache
def _get_output_parser() -> OutputParser:
    return OutputParser()


def _seed_demo_data() -> None:
    user_repo = _get_user_repository()
    if user_repo._store:
        return

    profile_repo = _get_profile_repository()
    journey_repo = _get_journey_repository()

    profile = get_demo_profile()
    profile_repo._store[profile.id] = profile
    profile_repo._snapshots[profile.id] = profile_repo._snapshots.get(profile.id) or __import__(
        "app.models.profile_snapshot", fromlist=["ProfileSnapshot"]
    ).ProfileSnapshot.from_profile(profile)

    journey = get_demo_journey()
    journey_repo._store[journey.id] = journey

    for user in get_demo_users(hash_password):
        user_repo._store[user.id] = user


@lru_cache
def _get_auth_service() -> AuthService:
    _seed_demo_data()
    return AuthService(_get_user_repository(), get_settings())


@lru_cache
def _get_profile_analysis_engine() -> ProfileAnalysisEngine:
    return ProfileAnalysisEngine(
        _get_prompt_builder(),
        _get_output_parser(),
        get_llm_provider(),
    )


@lru_cache
def _get_journey_engine() -> JourneyEngine:
    return JourneyEngine(
        _get_prompt_builder(),
        _get_output_parser(),
        get_llm_provider(),
    )


@lru_cache
def _get_mentor_engine() -> MentorEngine:
    return MentorEngine(
        _get_prompt_builder(),
        _get_output_parser(),
        get_llm_provider(),
    )


@lru_cache
def _get_faq_engine() -> FAQEngine:
    return FAQEngine(
        _get_prompt_builder(),
        _get_output_parser(),
        get_llm_provider(),
        knowledge_repository=_get_knowledge_repository(),
    )


@lru_cache
def _get_regeneration_engine() -> RegenerationEngine:
    return RegenerationEngine(
        _get_prompt_builder(),
        _get_output_parser(),
        get_llm_provider(),
    )


@lru_cache
def _get_journey_builder() -> JourneyBuilder:
    return JourneyBuilder(_get_journey_repository())


@lru_cache
def _get_profile_service() -> ProfileService:
    _seed_demo_data()
    return ProfileService(
        _get_profile_repository(),
        _get_profile_analysis_engine(),
        _get_prompt_service(),
    )


@lru_cache
def _get_journey_service() -> JourneyService:
    _seed_demo_data()
    return JourneyService(
        _get_journey_repository(),
        _get_profile_repository(),
        _get_journey_engine(),
        _get_journey_builder(),
    )


@lru_cache
def _get_mentor_service() -> MentorService:
    _seed_demo_data()
    return MentorService(
        _get_journey_repository(),
        _get_profile_repository(),
        _get_mentor_engine(),
    )


@lru_cache
def _get_faq_service() -> FAQService:
    _seed_demo_data()
    return FAQService(
        _get_profile_repository(),
        _get_faq_engine(),
        _get_prompt_service(),
    )


@lru_cache
def _get_regeneration_service() -> RegenerationService:
    _seed_demo_data()
    return RegenerationService(
        _get_journey_repository(),
        _get_profile_repository(),
        _get_regeneration_engine(),
        _get_journey_builder(),
    )


@lru_cache
def _get_admin_service() -> AdminService:
    _seed_demo_data()
    return AdminService(
        _get_admin_repository(),
        _get_knowledge_repository(),
        _get_profile_repository(),
        _get_journey_repository(),
    )


def get_auth_controller() -> AuthController:
    return AuthController(_get_auth_service())


def get_profile_controller() -> ProfileController:
    return ProfileController(_get_profile_service())


def get_journey_controller() -> JourneyController:
    return JourneyController(_get_journey_service())


def get_mentor_controller() -> MentorController:
    return MentorController(_get_mentor_service())


def get_faq_controller() -> FAQController:
    return FAQController(_get_faq_service())


def get_regeneration_controller() -> RegenerationController:
    return RegenerationController(_get_regeneration_service())


def get_admin_controller() -> AdminController:
    return AdminController(_get_admin_service())


async def get_current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    if credentials is None or not credentials.credentials:
        raise AuthenticationError(message="Authentication required")
    return decode_access_token(credentials.credentials)


def require_roles(*roles: str) -> Callable[..., dict[str, Any]]:
    async def _require(claims: dict[str, Any] = Depends(get_current_claims)) -> dict[str, Any]:
        if claims.get("role") not in roles:
            raise AuthorizationError(
                message="You do not have permission to perform this action",
                details={"required_roles": list(roles), "role": claims.get("role")},
            )
        return claims

    return _require
