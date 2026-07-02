from app.config.config_manager import ConfigManager
from app.core.exceptions import ConfigurationError, LLMProviderError
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, config_manager: ConfigManager) -> None:
        self._config = config_manager
        self._client = None

    @property
    def provider_name(self) -> str:
        return "openai"

    def _get_client(self):
        """Lazily initialize the OpenAI async client."""
        if self._client is not None:
            return self._client

        api_key = self._config.settings.openai_api_key
        if not api_key:
            raise ConfigurationError(
                message="OPENAI_API_KEY is not configured",
                details={"provider": self.provider_name},
            )

        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ConfigurationError(
                message="OpenAI SDK is not installed",
                details={"provider": self.provider_name},
            ) from exc

        self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    async def is_available(self) -> bool:
        return bool(self._config.settings.openai_api_key)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion using the OpenAI API."""
        client = self._get_client()
        model = request.model or self._config.settings.openai_model

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[msg.model_dump() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as exc:
            logger.error("OpenAI generation failed: %s", exc)
            raise LLMProviderError(
                message="OpenAI generation failed",
                details={"provider": self.provider_name, "reason": str(exc)},
            ) from exc

        choice = response.choices[0]
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return LLMResponse(
            content=choice.message.content or "",
            model=model,
            provider=self.provider_name,
            usage=usage,
        )
