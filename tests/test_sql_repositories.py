"""Tests for SQLAlchemy repositories using an in-memory SQLite database."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.journey import JourneyStatus
from app.repositories.seed_data import get_demo_journey, get_demo_profile
from app.repositories.sql.journey_repository import SQLJourneyRepository
from app.repositories.sql.profile_repository import SQLProfileRepository
from app.repositories.sql.user_repository import SQLUserRepository


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.mark.asyncio
async def test_sql_profile_crud(session_factory):
    repo = SQLProfileRepository(session_factory)
    demo = get_demo_profile()

    created = await repo.create(demo.model_dump())
    assert created.name == demo.name

    fetched = await repo.get_by_id(demo.id)
    assert fetched is not None
    assert fetched.email == demo.email

    by_email = await repo.get_by_email(demo.email)
    assert by_email is not None

    updated = await repo.update(demo.id, {"team": "Data Platform"})
    assert updated is not None
    assert updated.team == "Data Platform"

    snapshot = await repo.get_snapshot(demo.id)
    assert snapshot is not None
    assert snapshot.team == demo.team  # snapshot captured original team


@pytest.mark.asyncio
async def test_sql_journey_crud(session_factory):
    repo = SQLJourneyRepository(session_factory)
    demo = get_demo_journey()

    created = await repo.create(demo.model_dump())
    assert created.total_days == demo.total_days

    fetched = await repo.get_by_id(demo.id)
    assert fetched is not None
    assert len(fetched.days) == len(demo.days)

    by_profile = await repo.get_by_profile_id(demo.profile_id)
    assert len(by_profile) == 1

    active = await repo.get_active_by_profile_id(demo.profile_id)
    assert active is not None

    updated = await repo.update(demo.id, {"status": JourneyStatus.SUPERSEDED})
    assert updated is not None
    assert updated.status == JourneyStatus.SUPERSEDED


@pytest.mark.asyncio
async def test_sql_user_crud(session_factory):
    repo = SQLUserRepository(session_factory)
    created = await repo.create(
        {
            "email": "db.user@example.com",
            "name": "DB User",
            "role": "manager",
            "hashed_password": "x",
        }
    )
    fetched = await repo.get_by_email("db.user@example.com")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.role.value == "manager"
