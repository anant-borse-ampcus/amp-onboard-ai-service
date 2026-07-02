from pydantic import BaseModel, Field

from app.models.faq import FAQAnswer, FAQSource


class FAQRequest(BaseModel):
    """Request DTO for FAQ question."""

    question: str = Field(..., min_length=3, max_length=500)
    profile_id: str | None = None
    journey_id: str | None = None


class FAQResponse(FAQAnswer):
    """Response DTO for FAQ answer."""

    pass
