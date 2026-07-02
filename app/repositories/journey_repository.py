from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import NotFoundError, RepositoryError
from app.models.journey import Journey
from app.repositories.base import BaseRepository


class JourneyRepository(BaseRepository[Journey]):
    """In-memory repository for onboarding journeys."""

    def __init__(self) -> None:
        self._store: dict[UUID, Journey] = {}

    async def get_by_id(self, entity_id: UUID) -> Journey | None:
        return self._store.get(entity_id)

    async def get_all(self) -> list[Journey]:
        return list(self._store.values())

    async def get_by_profile_id(self, profile_id: UUID) -> list[Journey]:
        return [j for j in self._store.values() if j.profile_id == profile_id]

    async def get_active_by_profile_id(self, profile_id: UUID) -> Journey | None:
        journeys = await self.get_by_profile_id(profile_id)
        active = [j for j in journeys if j.status.value in ("active", "draft")]
        if not active:
            return None
        return max(active, key=lambda j: j.version)

    async def create(self, data: dict[str, Any]) -> Journey:
        try:
            entity = Journey(**data)
            self._store[entity.id] = entity
            return entity
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create journey",
                details={"reason": str(exc)},
            ) from exc

    async def update(self, entity_id: UUID, data: dict[str, Any]) -> Journey | None:
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
            raise NotFoundError(message="Journey not found")
        del self._store[entity_id]
        return True

    async def ping(self) -> bool:
        return True
