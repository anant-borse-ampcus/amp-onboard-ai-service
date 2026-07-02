from uuid import UUID

from app.schemas.faq import FAQRequest, FAQResponse
from app.schemas.journey import (
    ChecklistToggleRequest,
    JourneyGenerateRequest,
    JourneyRegenerateRequest,
    JourneyResponse,
    ProgressResponse,
    TaskCompleteRequest,
)
from app.schemas.mentor import MentorRequest, MentorResponse
from app.schemas.profile import (
    ProfileAnalysisResponse,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.schemas.regeneration import JourneyComparisonResponse
from app.services.faq_service import FAQService
from app.services.journey_service import JourneyService
from app.services.mentor_service import MentorService
from app.services.profile_service import ProfileService
from app.services.regeneration_service import RegenerationService


class ProfileController:
    def __init__(self, service: ProfileService) -> None:
        self._service = service

    async def create(self, request: ProfileCreateRequest) -> ProfileResponse:
        return await self._service.create_profile(request)

    async def list_all(self) -> list[ProfileResponse]:
        return await self._service.list_profiles()

    async def get(self, profile_id: UUID) -> ProfileResponse:
        return await self._service.get_profile(profile_id)

    async def update(self, profile_id: UUID, request: ProfileUpdateRequest) -> ProfileResponse:
        return await self._service.update_profile(profile_id, request)

    async def analyze(self, profile_id: UUID) -> ProfileAnalysisResponse:
        return await self._service.analyze_profile(profile_id)


class JourneyController:
    def __init__(self, service: JourneyService) -> None:
        self._service = service

    async def generate(self, request: JourneyGenerateRequest) -> JourneyResponse:
        return await self._service.generate_journey(request)

    async def get(self, journey_id: UUID) -> JourneyResponse:
        return await self._service.get_journey(journey_id)

    async def list_by_profile(self, profile_id: UUID) -> list[JourneyResponse]:
        return await self._service.get_journeys_by_profile(profile_id)

    async def activate(self, journey_id: UUID) -> JourneyResponse:
        return await self._service.activate_journey(journey_id)

    async def complete_task(
        self, journey_id: UUID, task_id: UUID, request: TaskCompleteRequest
    ) -> JourneyResponse:
        return await self._service.complete_task(journey_id, task_id, request)

    async def toggle_checklist(
        self,
        journey_id: UUID,
        task_id: UUID,
        checklist_id: UUID,
        request: ChecklistToggleRequest,
    ) -> JourneyResponse:
        return await self._service.toggle_checklist_item(
            journey_id, task_id, checklist_id, request
        )

    async def get_progress(self, profile_id: UUID) -> ProgressResponse:
        return await self._service.get_progress(profile_id)


class MentorController:
    def __init__(self, service: MentorService) -> None:
        self._service = service

    async def get_guidance(self, request: MentorRequest) -> MentorResponse:
        return await self._service.get_guidance(request)


class FAQController:
    def __init__(self, service: FAQService) -> None:
        self._service = service

    async def ask(self, request: FAQRequest) -> FAQResponse:
        return await self._service.ask(request)


class RegenerationController:
    def __init__(self, service: RegenerationService) -> None:
        self._service = service

    async def regenerate(self, request: JourneyRegenerateRequest) -> JourneyResponse:
        return await self._service.regenerate(request)

    async def compare(
        self, previous_id: UUID, current_id: UUID
    ) -> JourneyComparisonResponse:
        return await self._service.compare(previous_id, current_id)
