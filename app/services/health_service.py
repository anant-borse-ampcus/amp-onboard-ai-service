from app.config.config_manager import ConfigManager
from app.repositories.base import BaseRepository
from app.schemas.health import HealthResponse


class HealthService:
    """Service layer for health check operations."""

    def __init__(self, config_manager: ConfigManager, repository: BaseRepository) -> None:
        self._config_manager = config_manager
        self._repository = repository

    async def check_health(self) -> HealthResponse:
        """Perform health check against dependencies."""
        repository_ok = await self._repository.ping()
        settings = self._config_manager.settings

        return HealthResponse(
            status="healthy" if repository_ok else "degraded",
            service=settings.app_name,
            version=settings.app_version,
            environment=settings.app_env,
            repository="connected" if repository_ok else "disconnected",
        )
