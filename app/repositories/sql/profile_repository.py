from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.exceptions import NotFoundError, RepositoryError
from app.db.models import ProfileORM
from app.models.profile import EmployeeProfile, ExperienceLevel, LearningStyle
from app.models.profile_snapshot import ProfileSnapshot


def _to_domain(row: ProfileORM) -> EmployeeProfile:
    return EmployeeProfile(
        id=UUID(row.id),
        name=row.name,
        email=row.email,
        role=row.role,
        team=row.team,
        experience_level=ExperienceLevel(row.experience_level),
        skills=list(row.skills or []),
        learning_style=LearningStyle(row.learning_style),
        start_date=row.start_date or "",
        manager_notes=row.manager_notes or "",
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SQLProfileRepository:
    """SQLAlchemy-backed repository for employee profiles."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def get_by_id(self, entity_id: UUID) -> EmployeeProfile | None:
        async with self._session_factory() as session:
            row = await session.get(ProfileORM, str(entity_id))
            return _to_domain(row) if row else None

    async def get_by_email(self, email: str) -> EmployeeProfile | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProfileORM).where(ProfileORM.email == email)
            )
            row = result.scalar_one_or_none()
            return _to_domain(row) if row else None

    async def get_all(self) -> list[EmployeeProfile]:
        async with self._session_factory() as session:
            result = await session.execute(select(ProfileORM))
            return [_to_domain(r) for r in result.scalars().all()]

    async def create(self, data: dict[str, Any]) -> EmployeeProfile:
        try:
            entity = EmployeeProfile(**data)
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create profile", details={"reason": str(exc)}
            ) from exc

        async with self._session_factory() as session:
            row = ProfileORM(
                id=str(entity.id),
                name=entity.name,
                email=entity.email,
                role=entity.role,
                team=entity.team,
                experience_level=entity.experience_level.value,
                skills=list(entity.skills),
                learning_style=entity.learning_style.value,
                start_date=entity.start_date,
                manager_notes=entity.manager_notes,
                snapshot=ProfileSnapshot.from_profile(entity).model_dump(mode="json"),
            )
            session.add(row)
            await session.commit()
        return entity

    async def update(self, entity_id: UUID, data: dict[str, Any]) -> EmployeeProfile | None:
        async with self._session_factory() as session:
            row = await session.get(ProfileORM, str(entity_id))
            if row is None:
                return None
            if row.snapshot is None:
                row.snapshot = ProfileSnapshot.from_profile(
                    _to_domain(row)
                ).model_dump(mode="json")
            for key, value in data.items():
                if key in ("experience_level", "learning_style") and value is not None:
                    value = value.value if hasattr(value, "value") else value
                if hasattr(row, key):
                    setattr(row, key, value)
            await session.commit()
            await session.refresh(row)
            return _to_domain(row)

    async def get_snapshot(self, entity_id: UUID) -> ProfileSnapshot | None:
        async with self._session_factory() as session:
            row = await session.get(ProfileORM, str(entity_id))
            if row is None or row.snapshot is None:
                return None
            return ProfileSnapshot.model_validate(row.snapshot)

    async def save_snapshot(self, profile: EmployeeProfile) -> ProfileSnapshot:
        snapshot = ProfileSnapshot.from_profile(profile)
        async with self._session_factory() as session:
            row = await session.get(ProfileORM, str(profile.id))
            if row is not None:
                row.snapshot = snapshot.model_dump(mode="json")
                await session.commit()
        return snapshot

    async def delete(self, entity_id: UUID) -> bool:
        async with self._session_factory() as session:
            row = await session.get(ProfileORM, str(entity_id))
            if row is None:
                raise NotFoundError(message="Profile not found")
            await session.delete(row)
            await session.commit()
        return True

    async def ping(self) -> bool:
        async with self._session_factory() as session:
            await session.execute(select(ProfileORM).limit(1))
        return True
