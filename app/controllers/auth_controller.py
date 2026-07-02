from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService


class AuthController:
    """Controller for authentication endpoints."""

    def __init__(self, service: AuthService) -> None:
        self._service = service

    async def register(self, request: RegisterRequest) -> TokenResponse:
        return await self._service.register(request)

    async def login(self, request: LoginRequest) -> TokenResponse:
        return await self._service.login(request)

    async def me(self, user_id: str) -> UserResponse:
        return await self._service.get_current_user(user_id)
