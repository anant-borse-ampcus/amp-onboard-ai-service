from pydantic import BaseModel, EmailStr, Field

from app.models.profile import ExperienceLevel, LearningStyle


class ProfileCreateRequest(BaseModel):
    """Request DTO for creating an employee profile."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: str = Field(..., min_length=2, max_length=100)
    team: str = Field(..., min_length=2, max_length=100)
    experience_level: ExperienceLevel = ExperienceLevel.MID
    skills: list[str] = Field(default_factory=list)
    learning_style: LearningStyle = LearningStyle.HANDS_ON
    start_date: str = ""
    manager_notes: str = ""


class ProfileUpdateRequest(BaseModel):
    """Request DTO for updating an employee profile."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    role: str | None = Field(default=None, min_length=2, max_length=100)
    team: str | None = Field(default=None, min_length=2, max_length=100)
    experience_level: ExperienceLevel | None = None
    skills: list[str] | None = None
    learning_style: LearningStyle | None = None
    start_date: str | None = None
    manager_notes: str | None = None


class ProfileResponse(BaseModel):
    """Response DTO for employee profile."""

    id: str
    name: str
    email: str
    role: str
    team: str
    experience_level: ExperienceLevel
    skills: list[str]
    learning_style: LearningStyle
    start_date: str
    manager_notes: str
    created_at: str
    updated_at: str


class ProfileAnalysisResponse(BaseModel):
    """Mock AI profile analysis response."""

    profile_id: str
    strengths: list[str]
    focus_areas: list[str]
    recommended_pace: str
    summary: str
