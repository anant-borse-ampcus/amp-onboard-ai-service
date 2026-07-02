from fastapi import APIRouter, Depends

from app.controllers.auth_controller import AuthController
from app.core.dependencies import get_auth_controller, get_current_claims
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: RegisterRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> TokenResponse:
    return await controller.register(request)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> TokenResponse:
    return await controller.login(request)


@router.get("/me", response_model=UserResponse)
async def me(
    claims: dict = Depends(get_current_claims),
    controller: AuthController = Depends(get_auth_controller),
) -> UserResponse:
    return await controller.me(claims["sub"])
