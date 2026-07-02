from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.exceptions import RepositoryError
from app.db.models import UserORM
from app.models.user import User, UserRole


def _to_domain(row: UserORM) -> User:
    return User(
        id=UUID(row.id),
        email=row.email,
        name=row.name,
        role=UserRole(row.role),
        hashed_password=row.hashed_password,
        profile_id=row.profile_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SQLUserRepository:
    """SQLAlchemy-backed repository for users."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def get_by_id(self, entity_id: UUID) -> User | None:
        async with self._session_factory() as session:
            row = await session.get(UserORM, str(entity_id))
            return _to_domain(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM).where(UserORM.email == email)
            )
            row = result.scalar_one_or_none()
            return _to_domain(row) if row else None

    async def create(self, data: dict[str, Any]) -> User:
        try:
            entity = User(**data)
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create user", details={"reason": str(exc)}
            ) from exc

        async with self._session_factory() as session:
            row = UserORM(
                id=str(entity.id),
                email=entity.email,
                name=entity.name,
                role=entity.role.value,
                hashed_password=entity.hashed_password,
                profile_id=entity.profile_id,
            )
            session.add(row)
            await session.commit()
        return entity

    async def ping(self) -> bool:
        async with self._session_factory() as session:
            await session.execute(select(UserORM).limit(1))
        return True
