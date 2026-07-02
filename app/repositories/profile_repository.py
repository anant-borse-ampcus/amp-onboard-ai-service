from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import NotFoundError, RepositoryError
from app.models.profile import EmployeeProfile
from app.models.profile_snapshot import ProfileSnapshot
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[EmployeeProfile]):
    """In-memory repository for employee profiles."""

    def __init__(self) -> None:
        self._store: dict[UUID, EmployeeProfile] = {}
        self._snapshots: dict[UUID, ProfileSnapshot] = {}

    async def get_by_id(self, entity_id: UUID) -> EmployeeProfile | None:
        return self._store.get(entity_id)

    async def get_by_email(self, email: str) -> EmployeeProfile | None:
        for profile in self._store.values():
            if profile.email.lower() == email.lower():
                return profile
        return None

    async def get_all(self) -> list[EmployeeProfile]:
        return list(self._store.values())

    async def create(self, data: dict[str, Any]) -> EmployeeProfile:
        try:
            entity = EmployeeProfile(**data)
            self._store[entity.id] = entity
            self._snapshots[entity.id] = ProfileSnapshot.from_profile(entity)
            return entity
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create profile",
                details={"reason": str(exc)},
            ) from exc

    async def update(self, entity_id: UUID, data: dict[str, Any]) -> EmployeeProfile | None:
        entity = self._store.get(entity_id)
        if entity is None:
            return None

        if entity_id not in self._snapshots:
            self._snapshots[entity_id] = ProfileSnapshot.from_profile(entity)

        updated = entity.model_copy(
            update={**data, "updated_at": datetime.now(UTC)},
        )
        self._store[entity_id] = updated
        return updated

    async def get_snapshot(self, entity_id: UUID) -> ProfileSnapshot | None:
        return self._snapshots.get(entity_id)

    async def save_snapshot(self, profile: EmployeeProfile) -> ProfileSnapshot:
        snapshot = ProfileSnapshot.from_profile(profile)
        self._snapshots[profile.id] = snapshot
        return snapshot

    async def delete(self, entity_id: UUID) -> bool:
        if entity_id not in self._store:
            raise NotFoundError(message="Profile not found")
        del self._store[entity_id]
        self._snapshots.pop(entity_id, None)
        return True

    async def ping(self) -> bool:
        return True
