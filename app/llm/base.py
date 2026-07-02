from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """A single message in an LLM conversation."""

    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class LLMRequest(BaseModel):
    """Standardized LLM generation request."""

    messages: list[LLMMessage]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Standardized LLM generation response."""

    content: str
    model: str
    provider: str
    usage: dict[str, int] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM provider implementations."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion from the given request."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Check whether the provider is configured and reachable."""
