"""Pydantic schemas for validated LLM structured outputs."""

from pydantic import BaseModel, Field


class LLMChecklistItemOutput(BaseModel):
    title: str = Field(..., min_length=1)


class LLMTaskOutput(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    task_type: str = "learning"
    estimated_duration_minutes: int = Field(default=60, ge=15, le=480)
    checklist_items: list[LLMChecklistItemOutput] = Field(default_factory=list)


class LLMDayOutput(BaseModel):
    day_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1)
    description: str = ""
    tasks: list[LLMTaskOutput] = Field(default_factory=list)


class JourneyGenerationOutput(BaseModel):
    summary: str = ""
    days: list[LLMDayOutput] = Field(default_factory=list)


class ProfileAnalysisOutput(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    focus_areas: list[str] = Field(default_factory=list)
    recommended_pace: str = ""
    summary: str = ""


class MentorGuidanceOutput(BaseModel):
    purpose: str = ""
    learning_outcome: str = ""
    estimated_duration: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)


class FAQSourceOutput(BaseModel):
    title: str = ""
    url: str = ""
    excerpt: str = ""


class FAQAnswerOutput(BaseModel):
    question: str = ""
    answer: str = ""
    sources: list[FAQSourceOutput] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    fallback: bool = False


class RegenerationTaskOutput(BaseModel):
    title: str = ""
    description: str = ""
    task_type: str = "learning"
    estimated_duration_minutes: int = 60
    previous_title: str = ""
    reason: str = ""


class JourneyRegenerationOutput(BaseModel):
    added: list[RegenerationTaskOutput] = Field(default_factory=list)
    modified: list[RegenerationTaskOutput] = Field(default_factory=list)
    removed: list[RegenerationTaskOutput] = Field(default_factory=list)
    summary: str = ""
