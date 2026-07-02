from app.config.config_manager import ConfigManager
from app.core.exceptions import LLMProviderError
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider placeholder for future implementation."""

    def __init__(self, config_manager: ConfigManager) -> None:
        self._config = config_manager

    @property
    def provider_name(self) -> str:
        return "groq"

    async def is_available(self) -> bool:
        return bool(self._config.settings.groq_api_key)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Placeholder: Groq provider is not yet implemented."""
        logger.warning(
            "Groq provider generate() called but implementation is pending",
            extra={"model": request.model or self._config.settings.groq_model},
        )
        raise LLMProviderError(
            message="Groq provider is not yet implemented",
            details={
                "provider": self.provider_name,
                "status": "placeholder",
                "note": "Implement Groq API integration in Development Phase 1",
            },
        )
