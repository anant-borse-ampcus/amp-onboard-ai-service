from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.engines.profile_engine import ProfileAnalysisEngine
from app.models.profile import EmployeeProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import (
    ProfileAnalysisResponse,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.prompt_service import PromptService
from app.utils.mappers import profile_to_response


class ProfileService:
    """Service for employee profile management."""

    def __init__(
        self,
        repository: ProfileRepository,
        analysis_engine: ProfileAnalysisEngine,
        prompt_service: PromptService,
    ) -> None:
        self._repository = repository
        self._analysis_engine = analysis_engine
        self._prompt_service = prompt_service

    async def create_profile(self, request: ProfileCreateRequest) -> ProfileResponse:
        existing = await self._repository.get_by_email(request.email)
        if existing:
            raise ConflictError(
                message="Profile with this email already exists",
                details={"email": request.email},
            )

        profile = await self._repository.create(request.model_dump())
        return profile_to_response(profile)

    async def get_profile(self, profile_id: UUID) -> ProfileResponse:
        profile = await self._repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundError(message="Profile not found", details={"id": str(profile_id)})
        return profile_to_response(profile)

    async def list_profiles(self) -> list[ProfileResponse]:
        profiles = await self._repository.get_all()
        return [profile_to_response(p) for p in profiles]

    async def update_profile(
        self, profile_id: UUID, request: ProfileUpdateRequest
    ) -> ProfileResponse:
        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError(message="No fields provided for update")

        existing = await self._repository.get_by_id(profile_id)
        if not existing:
            raise NotFoundError(message="Profile not found", details={"id": str(profile_id)})

        profile = await self._repository.update(profile_id, update_data)
        if not profile:
            raise NotFoundError(message="Profile not found", details={"id": str(profile_id)})
        return profile_to_response(profile)

    async def analyze_profile(self, profile_id: UUID) -> ProfileAnalysisResponse:
        profile = await self._get_profile_entity(profile_id)
        output = await self._analysis_engine.analyze(profile)

        return ProfileAnalysisResponse(
            profile_id=str(profile_id),
            strengths=output.strengths,
            focus_areas=output.focus_areas,
            recommended_pace=output.recommended_pace,
            summary=output.summary,
        )

    async def _get_profile_entity(self, profile_id: UUID) -> EmployeeProfile:
        profile = await self._repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundError(message="Profile not found", details={"id": str(profile_id)})
        return profile
