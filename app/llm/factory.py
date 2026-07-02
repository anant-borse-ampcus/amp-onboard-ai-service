from app.config.config_manager import ConfigManager
from app.core.exceptions import ConfigurationError, LLMProviderError
from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse
from app.llm.providers.groq_provider import GroqProvider
from app.llm.providers.mock_provider import MockLLMProvider
from app.llm.providers.openai_provider import OpenAIProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances based on configuration."""

    def __init__(self, config_manager: ConfigManager) -> None:
        self._config_manager = config_manager

    def create(self) -> BaseLLMProvider:
        """Instantiate the configured LLM provider."""
        provider = self._config_manager.llm_provider

        if provider == "mock":
            return MockLLMProvider(self._config_manager)
        if provider == "openai":
            return OpenAIProvider(self._config_manager)
        if provider == "groq":
            return GroqProvider(self._config_manager)

        raise ConfigurationError(
            message=f"Unsupported LLM provider: {provider}",
            details={"supported_providers": ["mock", "openai", "groq"]},
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Convenience method to generate via the configured provider."""
        provider = self.create()
        if not await provider.is_available():
            raise LLMProviderError(
                message=f"LLM provider '{provider.provider_name}' is not available",
            )
        return await provider.generate(request)
