import pytest

from app.config.config_manager import ConfigManager
from app.config.settings import Settings
from app.core.exceptions import AppException, NotFoundError, LLMProviderError, ValidationError
from app.llm.base import LLMMessage, LLMRequest
from app.llm.factory import LLMProviderFactory
from app.llm.providers.groq_provider import GroqProvider
from app.llm.providers.openai_provider import OpenAIProvider
from app.repositories.mock_in_memory import MockInMemoryRepository


@pytest.mark.asyncio
async def test_mock_repository_crud():
    repo = MockInMemoryRepository()

    entity = await repo.create({"name": "test", "value": "hello"})
    assert entity.name == "test"
    assert entity.value == "hello"

    fetched = await repo.get_by_id(entity.id)
    assert fetched is not None
    assert fetched.name == "test"

    all_entities = await repo.get_all()
    assert len(all_entities) == 1

    updated = await repo.update(entity.id, {"value": "world"})
    assert updated is not None
    assert updated.value == "world"

    deleted = await repo.delete(entity.id)
    assert deleted is True

    assert await repo.get_by_id(entity.id) is None


@pytest.mark.asyncio
async def test_mock_repository_delete_not_found():
    from uuid import uuid4

    repo = MockInMemoryRepository()
    with pytest.raises(NotFoundError):
        await repo.delete(uuid4())


@pytest.mark.asyncio
async def test_mock_repository_ping():
    repo = MockInMemoryRepository()
    assert await repo.ping() is True


def test_config_manager_defaults():
    settings = Settings()
    manager = ConfigManager(settings)

    assert manager.app_name == "AMP Onboard AI Service"
    assert manager.app_version == "0.1.0"
    assert manager.llm_provider == "openai"


def test_config_manager_openai_llm_config():
    settings = Settings(openai_api_key="sk-test", openai_model="gpt-4o")
    manager = ConfigManager(settings)
    config = manager.get_llm_config()

    assert config["provider"] == "openai"
    assert config["api_key"] == "sk-test"
    assert config["model"] == "gpt-4o"


def test_config_manager_groq_llm_config():
    settings = Settings(llm_provider="groq", groq_api_key="gsk-test", groq_model="llama-test")
    manager = ConfigManager(settings)
    config = manager.get_llm_config()

    assert config["provider"] == "groq"
    assert config["api_key"] == "gsk-test"
    assert config["model"] == "llama-test"


def test_llm_factory_creates_openai_provider():
    settings = Settings(llm_provider="openai")
    factory = LLMProviderFactory(ConfigManager(settings))
    provider = factory.create()
    assert isinstance(provider, OpenAIProvider)
    assert provider.provider_name == "openai"


def test_llm_factory_creates_groq_provider():
    settings = Settings(llm_provider="groq")
    factory = LLMProviderFactory(ConfigManager(settings))
    provider = factory.create()
    assert isinstance(provider, GroqProvider)
    assert provider.provider_name == "groq"


@pytest.mark.asyncio
async def test_openai_provider_not_available_without_key():
    settings = Settings(llm_provider="openai", openai_api_key="")
    provider = OpenAIProvider(ConfigManager(settings))
    assert await provider.is_available() is False


@pytest.mark.asyncio
async def test_groq_provider_not_available_without_key():
    settings = Settings(llm_provider="groq", groq_api_key="")
    provider = GroqProvider(ConfigManager(settings))
    assert await provider.is_available() is False


@pytest.mark.asyncio
async def test_groq_provider_generate_raises_placeholder_error():
    settings = Settings(llm_provider="groq", groq_api_key="gsk-test")
    provider = GroqProvider(ConfigManager(settings))
    request = LLMRequest(messages=[LLMMessage(role="user", content="hi")])

    with pytest.raises(LLMProviderError) as exc_info:
        await provider.generate(request)

    assert exc_info.value.error_code == "LLM_PROVIDER_ERROR"
    assert "not yet implemented" in exc_info.value.message.lower()


def test_app_exception_attributes():
    exc = ValidationError(message="Invalid input", details={"field": "name"})
    assert exc.status_code == 422
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.details == {"field": "name"}


def test_app_exception_base_defaults():
    exc = AppException()
    assert exc.status_code == 500
    assert exc.error_code == "INTERNAL_ERROR"
