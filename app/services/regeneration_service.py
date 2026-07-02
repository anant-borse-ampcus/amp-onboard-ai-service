from uuid import UUID

from app.core.exceptions import NotFoundError
from app.engines.regeneration_engine import RegenerationEngine
from app.models.journey import JourneyStatus
from app.models.profile_snapshot import ProfileSnapshot
from app.models.regeneration import ChangeType
from app.repositories.journey_repository import JourneyRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.journey import JourneyRegenerateRequest, JourneyResponse
from app.schemas.regeneration import JourneyComparisonResponse, TaskChangeResponse
from app.utils.journey_builder import JourneyBuilder
from app.utils.mappers import journey_to_response


class RegenerationService:
    """Service for journey regeneration and comparison."""

    def __init__(
        self,
        journey_repository: JourneyRepository,
        profile_repository: ProfileRepository,
        regeneration_engine: RegenerationEngine,
        journey_builder: JourneyBuilder,
    ) -> None:
        self._journey_repo = journey_repository
        self._profile_repo = profile_repository
        self._regeneration_engine = regeneration_engine
        self._journey_builder = journey_builder

    async def regenerate(self, request: JourneyRegenerateRequest) -> JourneyResponse:
        profile_id = UUID(request.profile_id)
        previous_id = UUID(request.previous_journey_id)

        profile = await self._profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundError(message="Profile not found", details={"id": request.profile_id})

        previous = await self._journey_repo.get_by_id(previous_id)
        if not previous:
            raise NotFoundError(
                message="Previous journey not found",
                details={"id": request.previous_journey_id},
            )

        snapshot = await self._profile_repo.get_snapshot(profile_id)
        if not snapshot:
            snapshot = ProfileSnapshot.from_profile(profile)

        diff = self._regeneration_engine.detect_changes(snapshot, profile)
        changes = await self._regeneration_engine.regenerate(profile, previous, diff)
        merged = self._regeneration_engine.apply_changes(previous, changes)

        new_journey = await self._journey_builder.build_from_dict(
            profile_id, merged, previous.total_days, JourneyStatus.ACTIVE
        )

        await self._journey_repo.update(previous_id, {"status": JourneyStatus.SUPERSEDED})
        await self._profile_repo.save_snapshot(profile)

        return journey_to_response(new_journey)

    async def compare(
        self, previous_journey_id: UUID, current_journey_id: UUID
    ) -> JourneyComparisonResponse:
        previous = await self._journey_repo.get_by_id(previous_journey_id)
        current = await self._journey_repo.get_by_id(current_journey_id)

        if not previous or not current:
            raise NotFoundError(message="One or both journeys not found")

        prev_tasks = {t.title: t for d in previous.days for t in d.tasks}
        curr_tasks = {t.title: t for d in current.days for t in d.tasks}

        added: list[TaskChangeResponse] = []
        modified: list[TaskChangeResponse] = []
        removed: list[TaskChangeResponse] = []

        for title, task in curr_tasks.items():
            if title not in prev_tasks:
                added.append(
                    TaskChangeResponse(
                        change_type=ChangeType.ADDED,
                        task_id=str(task.id),
                        task=task,
                        reason="New task added during regeneration",
                    )
                )
            elif prev_tasks[title].description != task.description:
                modified.append(
                    TaskChangeResponse(
                        change_type=ChangeType.MODIFIED,
                        task_id=str(task.id),
                        task=task,
                        previous_title=title,
                        reason="Task content updated during regeneration",
                    )
                )

        for title, task in prev_tasks.items():
            if title not in curr_tasks:
                removed.append(
                    TaskChangeResponse(
                        change_type=ChangeType.REMOVED,
                        task_id=str(task.id),
                        previous_title=title,
                        reason="Task removed during regeneration",
                    )
                )

        return JourneyComparisonResponse(
            previous_journey_id=str(previous_journey_id),
            current_journey_id=str(current_journey_id),
            added=added,
            modified=modified,
            removed=removed,
            summary=f"{len(added)} added, {len(modified)} modified, {len(removed)} removed",
        )
