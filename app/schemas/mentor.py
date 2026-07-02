from pydantic import BaseModel, Field

from app.models.mentor import MentorGuidance


class MentorRequest(BaseModel):
    """Request DTO for AI mentor guidance."""

    task_id: str
    profile_id: str
    journey_id: str


class MentorResponse(MentorGuidance):
    """Response DTO for AI mentor guidance."""

    task_id: str
    task_title: str
