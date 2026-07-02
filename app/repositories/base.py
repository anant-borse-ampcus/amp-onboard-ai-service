from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

from app.models.base import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(ABC, Generic[T]):
    """Abstract repository interface for data access."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Retrieve an entity by its identifier."""

    @abstractmethod
    async def get_all(self) -> list[T]:
        """Retrieve all entities."""

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> T:
        """Create a new entity."""

    @abstractmethod
    async def update(self, entity_id: UUID, data: dict[str, Any]) -> T | None:
        """Update an existing entity."""

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by identifier."""

    @abstractmethod
    async def ping(self) -> bool:
        """Verify repository connectivity."""
