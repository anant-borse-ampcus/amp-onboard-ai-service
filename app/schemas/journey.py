from pydantic import BaseModel, Field

from app.models.journey import JourneyStatus, TaskStatus, TaskType


class ChecklistItemResponse(BaseModel):
    """Response DTO for checklist item."""

    id: str
    title: str
    completed: bool


class JourneyTaskResponse(BaseModel):
    """Response DTO for journey task."""

    id: str
    title: str
    description: str
    task_type: TaskType
    estimated_duration_minutes: int
    status: TaskStatus
    checklist_items: list[ChecklistItemResponse] = Field(default_factory=list)


class JourneyDayResponse(BaseModel):
    """Response DTO for journey day."""

    id: str
    day_number: int
    title: str
    description: str
    tasks: list[JourneyTaskResponse] = Field(default_factory=list)


class JourneyResponse(BaseModel):
    """Response DTO for onboarding journey."""

    id: str
    profile_id: str
    version: int
    status: JourneyStatus
    days: list[JourneyDayResponse] = Field(default_factory=list)
    total_days: int
    summary: str
    created_at: str
    updated_at: str


class JourneyGenerateRequest(BaseModel):
    """Request DTO for journey generation."""

    profile_id: str
    total_days: int = Field(default=5, ge=3, le=14)


class JourneyRegenerateRequest(BaseModel):
    """Request DTO for journey regeneration."""

    profile_id: str
    previous_journey_id: str


class TaskCompleteRequest(BaseModel):
    """Request DTO for marking a task complete."""

    completed: bool = True


class ChecklistToggleRequest(BaseModel):
    """Request DTO for toggling a checklist item."""

    completed: bool = True


class ProgressResponse(BaseModel):
    """Response DTO for onboarding progress."""

    profile_id: str
    journey_id: str
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    current_day: int
    days_completed: int
