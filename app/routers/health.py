from fastapi import APIRouter, Depends

from app.controllers.health_controller import HealthController
from app.core.dependencies import get_health_service
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


def _get_controller(
    health_service: HealthService = Depends(get_health_service),
) -> HealthController:
    return HealthController(health_service=health_service)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status and dependency connectivity.",
)
async def health_check(
    controller: HealthController = Depends(_get_controller),
) -> HealthResponse:
    return await controller.get_health()
