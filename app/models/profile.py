from enum import StrEnum

from pydantic import Field

from app.models.base import BaseEntity


class ExperienceLevel(StrEnum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class LearningStyle(StrEnum):
    VISUAL = "visual"
    HANDS_ON = "hands_on"
    READING = "reading"
    COLLABORATIVE = "collaborative"


class EmployeeProfile(BaseEntity):
    """Employee onboarding profile domain entity."""

    name: str
    email: str
    role: str
    team: str
    experience_level: ExperienceLevel = ExperienceLevel.MID
    skills: list[str] = Field(default_factory=list)
    learning_style: LearningStyle = LearningStyle.HANDS_ON
    start_date: str = ""
    manager_notes: str = ""
