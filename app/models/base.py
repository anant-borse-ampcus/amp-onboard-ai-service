from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TimestampMixin(BaseModel):
    """Mixin providing created/updated timestamps."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BaseEntity(TimestampMixin):
    """Base domain entity for persistence models."""

    id: UUID = Field(default_factory=uuid4)

    def to_dict(self) -> dict[str, Any]:
        """Serialize entity to a plain dictionary."""
        return self.model_dump(mode="json")
