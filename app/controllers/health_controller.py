from app.schemas.health import HealthResponse
from app.services.health_service import HealthService


class HealthController:
    """Controller for health check endpoints (MVC layer)."""

    def __init__(self, health_service: HealthService) -> None:
        self._health_service = health_service

    async def get_health(self) -> HealthResponse:
        """Handle health check request."""
        return await self._health_service.check_health()
