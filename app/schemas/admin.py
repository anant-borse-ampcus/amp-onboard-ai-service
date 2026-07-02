from pydantic import BaseModel, Field

from app.models.admin import TemplateStatus


# --- Organization / Branding --- #
class OrganizationResponse(BaseModel):
    id: str
    name: str
    description: str
    primary_color: str
    logo_url: str
    timezone: str
    support_email: str


class OrganizationUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    primary_color: str | None = None
    logo_url: str | None = None
    timezone: str | None = None
    support_email: str | None = None


class PublicBrandingResponse(BaseModel):
    """Public branding fields for login and app shell theming."""

    name: str
    description: str
    primary_color: str
    logo_url: str


# --- AI Configuration --- #
class AIConfigResponse(BaseModel):
    id: str
    provider: str
    model: str
    temperature: float
    enabled: bool
    guardrails_enabled: bool


class AIConfigUpdateRequest(BaseModel):
    provider: str | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    enabled: bool | None = None
    guardrails_enabled: bool | None = None


# --- Templates --- #
class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    role: str
    duration_days: int
    status: TemplateStatus
    tags: list[str]


class TemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = ""
    role: str = ""
    duration_days: int = Field(default=5, ge=1, le=30)
    tags: list[str] = Field(default_factory=list)


class TemplateUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    role: str | None = None
    duration_days: int | None = Field(default=None, ge=1, le=30)
    tags: list[str] | None = None


# --- Departments --- #
class DepartmentResponse(BaseModel):
    id: str
    name: str
    description: str
    lead: str
    member_count: int


class DepartmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = ""
    lead: str = ""
    member_count: int = Field(default=0, ge=0)


# --- Company Resources --- #
class ResourceResponse(BaseModel):
    id: str
    title: str
    url: str
    category: str
    description: str


class ResourceCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=160)
    url: str = ""
    category: str = "general"
    description: str = ""


# --- Knowledge Base --- #
class KnowledgeResponse(BaseModel):
    id: str
    title: str
    answer: str
    keywords: list[str]
    url: str
    excerpt: str


class KnowledgeCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=160)
    answer: str = Field(..., min_length=2)
    keywords: list[str] = Field(default_factory=list)
    url: str = ""
    excerpt: str = ""


# --- Analytics --- #
class AnalyticsResponse(BaseModel):
    total_profiles: int
    total_journeys: int
    active_journeys: int
    completed_journeys: int
    total_tasks: int
    completed_tasks: int
    overall_completion_rate: float
    total_departments: int
    total_templates: int
    published_templates: int
    knowledge_entries: int
    average_journey_days: float
