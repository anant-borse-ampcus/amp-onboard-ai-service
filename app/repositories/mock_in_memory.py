from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import NotFoundError, RepositoryError
from app.models.base import BaseEntity
from app.repositories.base import BaseRepository


class MockEntity(BaseEntity):
    """Placeholder domain entity for baseline in-memory storage."""

    name: str = "mock"
    value: str = ""


class MockInMemoryRepository(BaseRepository[MockEntity]):
    """In-memory repository implementation for development and testing."""

    def __init__(self) -> None:
        self._store: dict[UUID, MockEntity] = {}

    async def get_by_id(self, entity_id: UUID) -> MockEntity | None:
        return self._store.get(entity_id)

    async def get_all(self) -> list[MockEntity]:
        return list(self._store.values())

    async def create(self, data: dict[str, Any]) -> MockEntity:
        try:
            entity = MockEntity(**data)
            self._store[entity.id] = entity
            return entity
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create entity in mock repository",
                details={"reason": str(exc)},
            ) from exc

    async def update(self, entity_id: UUID, data: dict[str, Any]) -> MockEntity | None:
        entity = self._store.get(entity_id)
        if entity is None:
            return None

        updated = entity.model_copy(
            update={**data, "updated_at": datetime.now(UTC)},
        )
        self._store[entity_id] = updated
        return updated

    async def delete(self, entity_id: UUID) -> bool:
        if entity_id not in self._store:
            raise NotFoundError(message="Entity not found in mock repository")
        del self._store[entity_id]
        return True

    async def ping(self) -> bool:
        return True
