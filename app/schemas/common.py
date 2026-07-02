from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error detail payload."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard API error response envelope."""

    error: ErrorDetail


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Human-readable message")
