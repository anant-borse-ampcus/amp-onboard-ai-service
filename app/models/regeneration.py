from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.journey import JourneyTask


class ChangeType(StrEnum):
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"


class TaskChange(BaseModel):
    """Represents a single task change during journey regeneration."""

    change_type: ChangeType
    task_id: UUID | None = None
    task: JourneyTask | None = None
    reason: str = ""
    previous_title: str = ""


class JourneyComparison(BaseModel):
    """Comparison between two journey versions."""

    previous_journey_id: UUID
    current_journey_id: UUID
    added: list[TaskChange] = Field(default_factory=list)
    modified: list[TaskChange] = Field(default_factory=list)
    removed: list[TaskChange] = Field(default_factory=list)
    summary: str = ""
