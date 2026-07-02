from uuid import UUID

from app.config.settings import Settings
from app.core.security import (
    AuthenticationError,
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepositoryProtocol
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        profile_id=user.profile_id,
    )


class AuthService:
    """Handles registration, login, and token issuance."""

    def __init__(self, repository: UserRepositoryProtocol, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    async def register(self, request: RegisterRequest) -> TokenResponse:
        existing = await self._repository.get_by_email(request.email)
        if existing:
            raise ConflictError(
                message="A user with this email already exists",
                details={"email": request.email},
            )

        user = await self._repository.create(
            {
                "email": request.email,
                "name": request.name,
                "role": request.role,
                "hashed_password": hash_password(request.password),
                "profile_id": request.profile_id,
            }
        )
        return self._issue_token(user)

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self._repository.get_by_email(request.email)
        if not user or not verify_password(request.password, user.hashed_password):
            raise AuthenticationError(message="Invalid email or password")
        return self._issue_token(user)

    async def get_current_user(self, user_id: str) -> UserResponse:
        user = await self._repository.get_by_id(UUID(user_id))
        if not user:
            raise NotFoundError(message="User not found")
        return _to_user_response(user)

    def _issue_token(self, user: User) -> TokenResponse:
        token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
            extra={"email": user.email, "profile_id": user.profile_id},
            settings=self._settings,
        )
        return TokenResponse(
            access_token=token,
            expires_in=self._settings.jwt_access_token_expire_minutes * 60,
            user=_to_user_response(user),
        )
