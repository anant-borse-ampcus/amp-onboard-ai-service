from typing import Any, Protocol
from uuid import UUID

from app.core.exceptions import RepositoryError
from app.models.user import User


class UserRepositoryProtocol(Protocol):
    async def get_by_id(self, entity_id: UUID) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def create(self, data: dict[str, Any]) -> User: ...
    async def ping(self) -> bool: ...


class InMemoryUserRepository:
    """In-memory repository for users."""

    def __init__(self) -> None:
        self._store: dict[UUID, User] = {}

    async def get_by_id(self, entity_id: UUID) -> User | None:
        return self._store.get(entity_id)

    async def get_by_email(self, email: str) -> User | None:
        for user in self._store.values():
            if user.email.lower() == email.lower():
                return user
        return None

    async def create(self, data: dict[str, Any]) -> User:
        try:
            entity = User(**data)
            self._store[entity.id] = entity
            return entity
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create user", details={"reason": str(exc)}
            ) from exc

    async def ping(self) -> bool:
        return True
