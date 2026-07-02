from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    """Request DTO for user registration."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.EMPLOYEE
    profile_id: str | None = None


class LoginRequest(BaseModel):
    """Request DTO for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Response DTO for a user."""

    id: str
    email: str
    name: str
    role: UserRole
    profile_id: str | None = None


class TokenResponse(BaseModel):
    """Response DTO for successful authentication."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
