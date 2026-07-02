"""Build domain journey entities from engine output."""

from uuid import UUID

from app.models.journey import (
    ChecklistItem,
    Journey,
    JourneyDay,
    JourneyStatus,
    JourneyTask,
    TaskType,
)
from app.repositories.journey_repository import JourneyRepository
from app.schemas.llm_outputs import JourneyGenerationOutput


class JourneyBuilder:
    """Builds and persists journey domain entities."""

    def __init__(self, journey_repository: JourneyRepository) -> None:
        self._journey_repo = journey_repository

    async def build_and_save(
        self,
        profile_id: UUID,
        output: JourneyGenerationOutput,
        total_days: int,
        status: JourneyStatus = JourneyStatus.DRAFT,
    ) -> Journey:
        existing = await self._journey_repo.get_by_profile_id(profile_id)
        version = max((j.version for j in existing), default=0) + 1

        days = []
        for day_data in output.days:
            tasks = []
            for task_data in day_data.tasks:
                checklist = [
                    ChecklistItem(title=ci.title if hasattr(ci, "title") else ci["title"])
                    for ci in task_data.checklist_items
                ]
                task_type = task_data.task_type
                try:
                    tt = TaskType(task_type)
                except ValueError:
                    tt = TaskType.LEARNING

                tasks.append(
                    JourneyTask(
                        title=task_data.title,
                        description=task_data.description,
                        task_type=tt,
                        estimated_duration_minutes=task_data.estimated_duration_minutes,
                        checklist_items=checklist,
                    )
                )
            days.append(
                JourneyDay(
                    day_number=day_data.day_number,
                    title=day_data.title,
                    description=day_data.description,
                    tasks=tasks,
                )
            )

        return await self._journey_repo.create({
            "profile_id": profile_id,
            "version": version,
            "status": status,
            "days": days,
            "total_days": total_days,
            "summary": output.summary,
        })

    async def build_from_dict(
        self,
        profile_id: UUID,
        data: dict,
        total_days: int,
        status: JourneyStatus = JourneyStatus.DRAFT,
    ) -> Journey:
        from app.schemas.llm_outputs import JourneyGenerationOutput

        output = JourneyGenerationOutput.model_validate(data)
        return await self.build_and_save(profile_id, output, total_days, status)
