from uuid import UUID

from fastapi import APIRouter, Depends

from app.controllers.onboarding_controller import (
    FAQController,
    JourneyController,
    MentorController,
    ProfileController,
    RegenerationController,
)
from app.core.dependencies import (
    get_current_claims,
    get_faq_controller,
    get_journey_controller,
    get_mentor_controller,
    get_profile_controller,
    get_regeneration_controller,
    require_roles,
)
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

router = APIRouter(prefix="/api/v1", tags=["Onboarding"])

# Manager-only actions manage profiles and journey lifecycle.
manager_only = Depends(require_roles("manager"))
# Reads and employee task actions require any authenticated user.
authenticated = Depends(get_current_claims)


@router.post(
    "/profiles",
    response_model=ProfileResponse,
    status_code=201,
    dependencies=[manager_only],
)
async def create_profile(
    request: ProfileCreateRequest,
    controller: ProfileController = Depends(get_profile_controller),
) -> ProfileResponse:
    return await controller.create(request)


@router.get("/profiles", response_model=list[ProfileResponse], dependencies=[manager_only])
async def list_profiles(
    controller: ProfileController = Depends(get_profile_controller),
) -> list[ProfileResponse]:
    return await controller.list_all()


@router.get("/profiles/{profile_id}", response_model=ProfileResponse, dependencies=[authenticated])
async def get_profile(
    profile_id: UUID,
    controller: ProfileController = Depends(get_profile_controller),
) -> ProfileResponse:
    return await controller.get(profile_id)


@router.put("/profiles/{profile_id}", response_model=ProfileResponse, dependencies=[manager_only])
async def update_profile(
    profile_id: UUID,
    request: ProfileUpdateRequest,
    controller: ProfileController = Depends(get_profile_controller),
) -> ProfileResponse:
    return await controller.update(profile_id, request)


@router.post(
    "/profiles/{profile_id}/analyze",
    response_model=ProfileAnalysisResponse,
    dependencies=[manager_only],
)
async def analyze_profile(
    profile_id: UUID,
    controller: ProfileController = Depends(get_profile_controller),
) -> ProfileAnalysisResponse:
    return await controller.analyze(profile_id)


@router.post(
    "/journeys/generate",
    response_model=JourneyResponse,
    status_code=201,
    dependencies=[manager_only],
)
async def generate_journey(
    request: JourneyGenerateRequest,
    controller: JourneyController = Depends(get_journey_controller),
) -> JourneyResponse:
    return await controller.generate(request)


@router.get("/journeys/{journey_id}", response_model=JourneyResponse, dependencies=[authenticated])
async def get_journey(
    journey_id: UUID,
    controller: JourneyController = Depends(get_journey_controller),
) -> JourneyResponse:
    return await controller.get(journey_id)


@router.get(
    "/journeys/profile/{profile_id}",
    response_model=list[JourneyResponse],
    dependencies=[authenticated],
)
async def list_journeys_by_profile(
    profile_id: UUID,
    controller: JourneyController = Depends(get_journey_controller),
) -> list[JourneyResponse]:
    return await controller.list_by_profile(profile_id)


@router.post(
    "/journeys/{journey_id}/activate",
    response_model=JourneyResponse,
    dependencies=[manager_only],
)
async def activate_journey(
    journey_id: UUID,
    controller: JourneyController = Depends(get_journey_controller),
) -> JourneyResponse:
    return await controller.activate(journey_id)


@router.patch(
    "/journeys/{journey_id}/tasks/{task_id}",
    response_model=JourneyResponse,
    dependencies=[authenticated],
)
async def complete_task(
    journey_id: UUID,
    task_id: UUID,
    request: TaskCompleteRequest,
    controller: JourneyController = Depends(get_journey_controller),
) -> JourneyResponse:
    return await controller.complete_task(journey_id, task_id, request)


@router.patch(
    "/journeys/{journey_id}/tasks/{task_id}/checklist/{checklist_id}",
    response_model=JourneyResponse,
    dependencies=[authenticated],
)
async def toggle_checklist_item(
    journey_id: UUID,
    task_id: UUID,
    checklist_id: UUID,
    request: ChecklistToggleRequest,
    controller: JourneyController = Depends(get_journey_controller),
) -> JourneyResponse:
    return await controller.toggle_checklist(journey_id, task_id, checklist_id, request)


@router.get(
    "/progress/profile/{profile_id}",
    response_model=ProgressResponse,
    dependencies=[authenticated],
)
async def get_progress(
    profile_id: UUID,
    controller: JourneyController = Depends(get_journey_controller),
) -> ProgressResponse:
    return await controller.get_progress(profile_id)


@router.post("/mentor/guidance", response_model=MentorResponse, dependencies=[authenticated])
async def get_mentor_guidance(
    request: MentorRequest,
    controller: MentorController = Depends(get_mentor_controller),
) -> MentorResponse:
    return await controller.get_guidance(request)


@router.post("/faq/ask", response_model=FAQResponse, dependencies=[authenticated])
async def ask_faq(
    request: FAQRequest,
    controller: FAQController = Depends(get_faq_controller),
) -> FAQResponse:
    return await controller.ask(request)


@router.post(
    "/journeys/regenerate",
    response_model=JourneyResponse,
    status_code=201,
    dependencies=[manager_only],
)
async def regenerate_journey(
    request: JourneyRegenerateRequest,
    controller: RegenerationController = Depends(get_regeneration_controller),
) -> JourneyResponse:
    return await controller.regenerate(request)


@router.get(
    "/journeys/compare/{previous_id}/{current_id}",
    response_model=JourneyComparisonResponse,
    dependencies=[authenticated],
)
async def compare_journeys(
    previous_id: UUID,
    current_id: UUID,
    controller: RegenerationController = Depends(get_regeneration_controller),
) -> JourneyComparisonResponse:
    return await controller.compare(previous_id, current_id)
