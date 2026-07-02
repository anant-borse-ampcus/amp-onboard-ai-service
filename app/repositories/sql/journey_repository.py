from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.exceptions import NotFoundError, RepositoryError
from app.db.models import JourneyORM
from app.models.journey import Journey


def _to_domain(row: JourneyORM) -> Journey:
    return Journey.model_validate(
        {
            "id": row.id,
            "profile_id": row.profile_id,
            "version": row.version,
            "status": row.status,
            "total_days": row.total_days,
            "summary": row.summary,
            "days": row.days or [],
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
    )


def _serialize_days(journey: Journey) -> list:
    return [day.model_dump(mode="json") for day in journey.days]


class SQLJourneyRepository:
    """SQLAlchemy-backed repository for onboarding journeys."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def get_by_id(self, entity_id: UUID) -> Journey | None:
        async with self._session_factory() as session:
            row = await session.get(JourneyORM, str(entity_id))
            return _to_domain(row) if row else None

    async def get_all(self) -> list[Journey]:
        async with self._session_factory() as session:
            result = await session.execute(select(JourneyORM))
            return [_to_domain(r) for r in result.scalars().all()]

    async def get_by_profile_id(self, profile_id: UUID) -> list[Journey]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(JourneyORM).where(JourneyORM.profile_id == str(profile_id))
            )
            return [_to_domain(r) for r in result.scalars().all()]

    async def get_active_by_profile_id(self, profile_id: UUID) -> Journey | None:
        journeys = await self.get_by_profile_id(profile_id)
        active = [j for j in journeys if j.status.value in ("active", "draft")]
        if not active:
            return None
        return max(active, key=lambda j: j.version)

    async def create(self, data: dict[str, Any]) -> Journey:
        try:
            entity = Journey(**data)
        except Exception as exc:
            raise RepositoryError(
                message="Failed to create journey", details={"reason": str(exc)}
            ) from exc

        async with self._session_factory() as session:
            row = JourneyORM(
                id=str(entity.id),
                profile_id=str(entity.profile_id),
                version=entity.version,
                status=entity.status.value,
                total_days=entity.total_days,
                summary=entity.summary,
                days=_serialize_days(entity),
            )
            session.add(row)
            await session.commit()
        return entity

    async def update(self, entity_id: UUID, data: dict[str, Any]) -> Journey | None:
        async with self._session_factory() as session:
            row = await session.get(JourneyORM, str(entity_id))
            if row is None:
                return None

            if "status" in data:
                status = data["status"]
                row.status = status.value if hasattr(status, "value") else status
            if "days" in data:
                days = data["days"]
                row.days = [
                    d.model_dump(mode="json") if hasattr(d, "model_dump") else d
                    for d in days
                ]
            if "summary" in data:
                row.summary = data["summary"]
            if "version" in data:
                row.version = data["version"]
            if "total_days" in data:
                row.total_days = data["total_days"]

            await session.commit()
            await session.refresh(row)
            return _to_domain(row)

    async def delete(self, entity_id: UUID) -> bool:
        async with self._session_factory() as session:
            row = await session.get(JourneyORM, str(entity_id))
            if row is None:
                raise NotFoundError(message="Journey not found")
            await session.delete(row)
            await session.commit()
        return True

    async def ping(self) -> bool:
        async with self._session_factory() as session:
            await session.execute(select(JourneyORM).limit(1))
        return True
