from pydantic import BaseModel, Field


class FAQSource(BaseModel):
    """Reference source for a grounded FAQ answer."""

    title: str
    url: str = ""
    excerpt: str = ""


class FAQAnswer(BaseModel):
    """Grounded FAQ response."""

    question: str
    answer: str
    sources: list[FAQSource] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    fallback: bool = False
