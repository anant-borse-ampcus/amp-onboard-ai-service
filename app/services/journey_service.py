from uuid import UUID

from app.core.exceptions import NotFoundError
from app.engines.journey_engine import JourneyEngine
from app.models.journey import JourneyStatus, TaskStatus
from app.repositories.journey_repository import JourneyRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.journey import (
    ChecklistToggleRequest,
    JourneyGenerateRequest,
    JourneyResponse,
    ProgressResponse,
    TaskCompleteRequest,
)
from app.utils.journey_builder import JourneyBuilder
from app.utils.mappers import journey_to_response


class JourneyService:
    """Service for onboarding journey management."""

    def __init__(
        self,
        journey_repository: JourneyRepository,
        profile_repository: ProfileRepository,
        journey_engine: JourneyEngine,
        journey_builder: JourneyBuilder,
    ) -> None:
        self._journey_repo = journey_repository
        self._profile_repo = profile_repository
        self._journey_engine = journey_engine
        self._journey_builder = journey_builder

    async def generate_journey(self, request: JourneyGenerateRequest) -> JourneyResponse:
        profile_id = UUID(request.profile_id)
        profile = await self._profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundError(message="Profile not found", details={"id": request.profile_id})

        output = await self._journey_engine.generate(profile, request.total_days)
        journey = await self._journey_builder.build_and_save(
            profile_id, output, request.total_days
        )
        return journey_to_response(journey)

    async def get_journey(self, journey_id: UUID) -> JourneyResponse:
        journey = await self._journey_repo.get_by_id(journey_id)
        if not journey:
            raise NotFoundError(message="Journey not found", details={"id": str(journey_id)})
        return journey_to_response(journey)

    async def get_journeys_by_profile(self, profile_id: UUID) -> list[JourneyResponse]:
        journeys = await self._journey_repo.get_by_profile_id(profile_id)
        return [journey_to_response(j) for j in journeys]

    async def activate_journey(self, journey_id: UUID) -> JourneyResponse:
        journey = await self._journey_repo.get_by_id(journey_id)
        if not journey:
            raise NotFoundError(message="Journey not found", details={"id": str(journey_id)})

        existing = await self._journey_repo.get_by_profile_id(journey.profile_id)
        for j in existing:
            if j.id != journey_id and j.status == JourneyStatus.ACTIVE:
                await self._journey_repo.update(j.id, {"status": JourneyStatus.SUPERSEDED})

        updated = await self._journey_repo.update(
            journey_id, {"status": JourneyStatus.ACTIVE}
        )
        return journey_to_response(updated)  # type: ignore[arg-type]

    async def complete_task(
        self, journey_id: UUID, task_id: UUID, request: TaskCompleteRequest
    ) -> JourneyResponse:
        journey = await self._journey_repo.get_by_id(journey_id)
        if not journey:
            raise NotFoundError(message="Journey not found", details={"id": str(journey_id)})

        updated_days = []
        task_found = False
        for day in journey.days:
            updated_tasks = []
            for task in day.tasks:
                if task.id == task_id:
                    task_found = True
                    new_status = TaskStatus.COMPLETED if request.completed else TaskStatus.PENDING
                    updated_tasks.append(task.model_copy(update={"status": new_status}))
                else:
                    updated_tasks.append(task)
            updated_days.append(day.model_copy(update={"tasks": updated_tasks}))

        if not task_found:
            raise NotFoundError(message="Task not found", details={"id": str(task_id)})

        updated = await self._journey_repo.update(journey_id, {"days": updated_days})
        return journey_to_response(updated)  # type: ignore[arg-type]

    async def toggle_checklist_item(
        self,
        journey_id: UUID,
        task_id: UUID,
        checklist_id: UUID,
        request: ChecklistToggleRequest,
    ) -> JourneyResponse:
        journey = await self._journey_repo.get_by_id(journey_id)
        if not journey:
            raise NotFoundError(message="Journey not found", details={"id": str(journey_id)})

        updated_days = []
        item_found = False
        for day in journey.days:
            updated_tasks = []
            for task in day.tasks:
                if task.id == task_id:
                    updated_checklist = []
                    for item in task.checklist_items:
                        if item.id == checklist_id:
                            item_found = True
                            updated_checklist.append(
                                item.model_copy(update={"completed": request.completed})
                            )
                        else:
                            updated_checklist.append(item)
                    updated_tasks.append(
                        task.model_copy(update={"checklist_items": updated_checklist})
                    )
                else:
                    updated_tasks.append(task)
            updated_days.append(day.model_copy(update={"tasks": updated_tasks}))

        if not item_found:
            raise NotFoundError(message="Checklist item not found", details={"id": str(checklist_id)})

        updated = await self._journey_repo.update(journey_id, {"days": updated_days})
        return journey_to_response(updated)  # type: ignore[arg-type]

    async def get_progress(self, profile_id: UUID) -> ProgressResponse:
        journey = await self._journey_repo.get_active_by_profile_id(profile_id)
        if not journey:
            raise NotFoundError(
                message="No active journey found for profile",
                details={"profile_id": str(profile_id)},
            )

        total_tasks = 0
        completed_tasks = 0
        days_completed = 0
        current_day = 1

        for day in journey.days:
            day_total = len(day.tasks)
            day_completed = sum(1 for t in day.tasks if t.status == TaskStatus.COMPLETED)
            total_tasks += day_total
            completed_tasks += day_completed

            if day_completed == day_total and day_total > 0:
                days_completed += 1
            elif day_completed < day_total:
                current_day = day.day_number

        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

        return ProgressResponse(
            profile_id=str(profile_id),
            journey_id=str(journey.id),
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            progress_percentage=round(progress, 1),
            current_day=current_day,
            days_completed=days_completed,
        )
