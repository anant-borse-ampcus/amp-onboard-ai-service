from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.models.base import BaseEntity


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskType(StrEnum):
    LEARNING = "learning"
    MEETING = "meeting"
    SETUP = "setup"
    PROJECT = "project"
    REVIEW = "review"


class ChecklistItem(BaseEntity):
    """Checklist item within a task."""

    title: str
    completed: bool = False


class JourneyTask(BaseEntity):
    """A single task within a journey day."""

    title: str
    description: str = ""
    task_type: TaskType = TaskType.LEARNING
    estimated_duration_minutes: int = 60
    status: TaskStatus = TaskStatus.PENDING
    checklist_items: list[ChecklistItem] = Field(default_factory=list)


class JourneyDay(BaseEntity):
    """A single day in an onboarding journey."""

    day_number: int
    title: str
    description: str = ""
    tasks: list[JourneyTask] = Field(default_factory=list)


class JourneyStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUPERSEDED = "superseded"


class Journey(BaseEntity):
    """Onboarding journey domain entity."""

    profile_id: UUID
    version: int = 1
    status: JourneyStatus = JourneyStatus.DRAFT
    days: list[JourneyDay] = Field(default_factory=list)
    total_days: int = 0
    summary: str = ""
