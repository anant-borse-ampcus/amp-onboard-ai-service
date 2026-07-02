from enum import StrEnum

from pydantic import Field

from app.models.base import BaseEntity


class UserRole(StrEnum):
    SYSTEM_ADMIN = "system_admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(BaseEntity):
    """Application user domain entity."""

    email: str
    name: str
    role: UserRole = UserRole.EMPLOYEE
    hashed_password: str = ""
    profile_id: str | None = Field(
        default=None, description="Linked employee profile id, if any"
    )
