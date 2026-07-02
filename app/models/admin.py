"""Domain entities for System Admin configuration and content."""

from enum import StrEnum

from pydantic import Field

from app.models.base import BaseEntity


class OrganizationConfig(BaseEntity):
    """Organization-wide configuration and branding."""

    name: str = "Acme Corp"
    description: str = "Building great products together."
    primary_color: str = "#4f46e5"
    logo_url: str = ""
    timezone: str = "UTC"
    support_email: str = "support@example.com"


class AIConfig(BaseEntity):
    """AI generation configuration managed by the system admin."""

    provider: str = "mock"
    model: str = "mock"
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    enabled: bool = True
    guardrails_enabled: bool = True


class TemplateStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class OnboardingTemplate(BaseEntity):
    """Reusable onboarding template that managers can base plans on."""

    name: str
    description: str = ""
    role: str = ""
    duration_days: int = 5
    status: TemplateStatus = TemplateStatus.DRAFT
    tags: list[str] = Field(default_factory=list)


class Department(BaseEntity):
    """Department / team within the organization."""

    name: str
    description: str = ""
    lead: str = ""
    member_count: int = 0


class CompanyResource(BaseEntity):
    """A company resource link surfaced during onboarding."""

    title: str
    url: str = ""
    category: str = "general"
    description: str = ""


class KnowledgeEntry(BaseEntity):
    """A grounded knowledge base entry used by the FAQ engine."""

    title: str
    answer: str
    keywords: list[str] = Field(default_factory=list)
    url: str = ""
    excerpt: str = ""

    def to_faq_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "answer": self.answer,
            "keywords": self.keywords,
            "url": self.url,
            "excerpt": self.excerpt,
        }
