from uuid import UUID

from app.core.exceptions import NotFoundError
from app.engines.mentor_engine import MentorEngine
from app.repositories.journey_repository import JourneyRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.mentor import MentorRequest, MentorResponse


class MentorService:
    """Service for AI mentor guidance."""

    def __init__(
        self,
        journey_repository: JourneyRepository,
        profile_repository: ProfileRepository,
        mentor_engine: MentorEngine,
    ) -> None:
        self._journey_repo = journey_repository
        self._profile_repo = profile_repository
        self._mentor_engine = mentor_engine

    async def get_guidance(self, request: MentorRequest) -> MentorResponse:
        journey_id = UUID(request.journey_id)
        profile_id = UUID(request.profile_id)
        task_id = UUID(request.task_id)

        journey = await self._journey_repo.get_by_id(journey_id)
        if not journey:
            raise NotFoundError(message="Journey not found", details={"id": request.journey_id})

        profile = await self._profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundError(message="Profile not found", details={"id": request.profile_id})

        task = None
        for day in journey.days:
            for t in day.tasks:
                if t.id == task_id:
                    task = t
                    break

        if not task:
            raise NotFoundError(message="Task not found", details={"id": request.task_id})

        output = await self._mentor_engine.get_guidance(profile, journey, task)

        return MentorResponse(
            task_id=request.task_id,
            task_title=task.title,
            purpose=output.purpose,
            learning_outcome=output.learning_outcome,
            estimated_duration=output.estimated_duration,
            prerequisites=output.prerequisites,
            tips=output.tips,
        )
