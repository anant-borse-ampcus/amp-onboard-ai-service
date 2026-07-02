"""Profile snapshot for change detection during regeneration."""

from pydantic import BaseModel, Field

from app.models.base import BaseEntity
from app.models.profile import EmployeeProfile, ExperienceLevel, LearningStyle


class ProfileSnapshot(BaseEntity):
    """Frozen profile state for detecting changes."""

    profile_id: str
    name: str
    role: str
    team: str
    experience_level: ExperienceLevel
    skills: list[str] = Field(default_factory=list)
    learning_style: LearningStyle

    @classmethod
    def from_profile(cls, profile: EmployeeProfile) -> "ProfileSnapshot":
        return cls(
            profile_id=str(profile.id),
            name=profile.name,
            role=profile.role,
            team=profile.team,
            experience_level=profile.experience_level,
            skills=list(profile.skills),
            learning_style=profile.learning_style,
        )


class ProfileDiff(BaseModel):
    """Detected changes between profile snapshots."""

    role_changed: bool = False
    team_changed: bool = False
    experience_changed: bool = False
    skills_changed: bool = False
    learning_style_changed: bool = False
    changed_fields: list[str] = Field(default_factory=list)
    previous_role: str = ""
    previous_team: str = ""
    previous_experience: str = ""
    previous_skills: str = ""
    current_role: str = ""
    current_team: str = ""
    current_experience: str = ""
    current_skills: str = ""

    @property
    def has_changes(self) -> bool:
        return len(self.changed_fields) > 0
