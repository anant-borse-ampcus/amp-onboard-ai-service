from pydantic import BaseModel, Field

from app.models.journey import JourneyTask
from app.models.regeneration import ChangeType


class TaskChangeResponse(BaseModel):
    """Response DTO for task change."""

    change_type: ChangeType
    task_id: str | None = None
    task: JourneyTask | None = None
    reason: str = ""
    previous_title: str = ""


class JourneyComparisonResponse(BaseModel):
    """Response DTO for journey comparison."""

    previous_journey_id: str
    current_journey_id: str
    added: list[TaskChangeResponse] = Field(default_factory=list)
    modified: list[TaskChangeResponse] = Field(default_factory=list)
    removed: list[TaskChangeResponse] = Field(default_factory=list)
    summary: str = ""
