from functools import lru_cache

from fastapi import Depends

from app.config.config_manager import ConfigManager, get_config_manager
from app.config.settings import Settings, get_settings
from app.llm.factory import LLMProviderFactory
from app.llm.base import BaseLLMProvider
from app.repositories.mock_in_memory import MockInMemoryRepository
from app.repositories.base import BaseRepository
from app.services.health_service import HealthService


def get_settings_dependency() -> Settings:
    """FastAPI dependency for application settings."""
    return get_settings()


def get_config_manager_dependency() -> ConfigManager:
    """FastAPI dependency for configuration manager."""
    return get_config_manager()


@lru_cache
def _get_mock_repository() -> MockInMemoryRepository:
    return MockInMemoryRepository()


def get_repository() -> BaseRepository:
    """FastAPI dependency for the default repository implementation."""
    return _get_mock_repository()


@lru_cache
def _get_llm_factory() -> LLMProviderFactory:
    return LLMProviderFactory(get_config_manager())


def get_llm_provider() -> BaseLLMProvider:
    """FastAPI dependency for the configured LLM provider."""
    return _get_llm_factory().create()


def get_health_service(
    config_manager: ConfigManager = Depends(get_config_manager_dependency),
    repository: BaseRepository = Depends(get_repository),
) -> HealthService:
    """FastAPI dependency for health check service."""
    return HealthService(config_manager=config_manager, repository=repository)
