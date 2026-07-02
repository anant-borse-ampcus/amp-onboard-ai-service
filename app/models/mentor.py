from pydantic import BaseModel, Field


class MentorGuidance(BaseModel):
    """AI mentor guidance for a specific task."""

    purpose: str
    learning_outcome: str
    estimated_duration: str
    prerequisites: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
