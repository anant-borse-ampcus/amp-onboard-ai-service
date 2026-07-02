from uuid import UUID

from app.models.admin import (
    CompanyResource,
    Department,
    KnowledgeEntry,
    OnboardingTemplate,
    TemplateStatus,
)
from app.models.journey import TaskStatus
from app.repositories.admin_repository import AdminRepository, KnowledgeRepository
from app.repositories.journey_repository import JourneyRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.admin import (
    AIConfigResponse,
    AIConfigUpdateRequest,
    AnalyticsResponse,
    DepartmentCreateRequest,
    DepartmentResponse,
    KnowledgeCreateRequest,
    KnowledgeResponse,
    OrganizationResponse,
    OrganizationUpdateRequest,
    ResourceCreateRequest,
    ResourceResponse,
    TemplateCreateRequest,
    TemplateResponse,
    TemplateUpdateRequest,
)


class AdminService:
    """Business logic for System Admin configuration, content, and analytics."""

    def __init__(
        self,
        admin_repository: AdminRepository,
        knowledge_repository: KnowledgeRepository,
        profile_repository: ProfileRepository,
        journey_repository: JourneyRepository,
    ) -> None:
        self._admin = admin_repository
        self._knowledge = knowledge_repository
        self._profiles = profile_repository
        self._journeys = journey_repository

    # --- Organization / Branding --- #
    def get_organization(self) -> OrganizationResponse:
        return self._org_to_response()

    def update_organization(self, request: OrganizationUpdateRequest) -> OrganizationResponse:
        self._admin.update_organization(request.model_dump(exclude_unset=True))
        return self._org_to_response()

    def _org_to_response(self) -> OrganizationResponse:
        org = self._admin.organization
        return OrganizationResponse(
            id=str(org.id),
            name=org.name,
            description=org.description,
            primary_color=org.primary_color,
            logo_url=org.logo_url,
            timezone=org.timezone,
            support_email=org.support_email,
        )

    # --- AI Configuration --- #
    def get_ai_config(self) -> AIConfigResponse:
        return self._ai_to_response()

    def update_ai_config(self, request: AIConfigUpdateRequest) -> AIConfigResponse:
        self._admin.update_ai_config(request.model_dump(exclude_unset=True))
        return self._ai_to_response()

    def _ai_to_response(self) -> AIConfigResponse:
        cfg = self._admin.ai_config
        return AIConfigResponse(
            id=str(cfg.id),
            provider=cfg.provider,
            model=cfg.model,
            temperature=cfg.temperature,
            enabled=cfg.enabled,
            guardrails_enabled=cfg.guardrails_enabled,
        )

    # --- Templates --- #
    def list_templates(self) -> list[TemplateResponse]:
        return [self._template_to_response(t) for t in self._admin.list_templates()]

    def create_template(self, request: TemplateCreateRequest) -> TemplateResponse:
        template = OnboardingTemplate(**request.model_dump())
        return self._template_to_response(self._admin.create_template(template))

    def update_template(
        self, template_id: UUID, request: TemplateUpdateRequest
    ) -> TemplateResponse:
        updated = self._admin.update_template(
            template_id, request.model_dump(exclude_unset=True)
        )
        return self._template_to_response(updated)

    def publish_template(self, template_id: UUID) -> TemplateResponse:
        updated = self._admin.update_template(
            template_id, {"status": TemplateStatus.PUBLISHED}
        )
        return self._template_to_response(updated)

    def delete_template(self, template_id: UUID) -> None:
        self._admin.delete_template(template_id)

    def _template_to_response(self, t: OnboardingTemplate) -> TemplateResponse:
        return TemplateResponse(
            id=str(t.id),
            name=t.name,
            description=t.description,
            role=t.role,
            duration_days=t.duration_days,
            status=t.status,
            tags=t.tags,
        )

    # --- Departments --- #
    def list_departments(self) -> list[DepartmentResponse]:
        return [self._department_to_response(d) for d in self._admin.list_departments()]

    def create_department(self, request: DepartmentCreateRequest) -> DepartmentResponse:
        department = Department(**request.model_dump())
        return self._department_to_response(self._admin.create_department(department))

    def delete_department(self, department_id: UUID) -> None:
        self._admin.delete_department(department_id)

    def _department_to_response(self, d: Department) -> DepartmentResponse:
        return DepartmentResponse(
            id=str(d.id),
            name=d.name,
            description=d.description,
            lead=d.lead,
            member_count=d.member_count,
        )

    # --- Company Resources --- #
    def list_resources(self) -> list[ResourceResponse]:
        return [self._resource_to_response(r) for r in self._admin.list_resources()]

    def create_resource(self, request: ResourceCreateRequest) -> ResourceResponse:
        resource = CompanyResource(**request.model_dump())
        return self._resource_to_response(self._admin.create_resource(resource))

    def delete_resource(self, resource_id: UUID) -> None:
        self._admin.delete_resource(resource_id)

    def _resource_to_response(self, r: CompanyResource) -> ResourceResponse:
        return ResourceResponse(
            id=str(r.id),
            title=r.title,
            url=r.url,
            category=r.category,
            description=r.description,
        )

    # --- Knowledge Base --- #
    def list_knowledge(self) -> list[KnowledgeResponse]:
        return [self._knowledge_to_response(e) for e in self._knowledge.all()]

    def create_knowledge(self, request: KnowledgeCreateRequest) -> KnowledgeResponse:
        entry = KnowledgeEntry(
            title=request.title,
            answer=request.answer,
            keywords=request.keywords,
            url=request.url,
            excerpt=request.excerpt or request.answer[:80],
        )
        return self._knowledge_to_response(self._knowledge.add(entry))

    def delete_knowledge(self, entry_id: UUID) -> None:
        self._knowledge.delete(entry_id)

    def _knowledge_to_response(self, e: KnowledgeEntry) -> KnowledgeResponse:
        return KnowledgeResponse(
            id=str(e.id),
            title=e.title,
            answer=e.answer,
            keywords=e.keywords,
            url=e.url,
            excerpt=e.excerpt,
        )

    # --- Analytics --- #
    async def get_analytics(self) -> AnalyticsResponse:
        profiles = await self._profiles.get_all()
        journeys = await self._journeys.get_all()

        total_tasks = 0
        completed_tasks = 0
        active = 0
        completed_journeys = 0
        total_days = 0

        for journey in journeys:
            total_days += journey.total_days
            if journey.status.value == "active":
                active += 1
            journey_tasks = [t for day in journey.days for t in day.tasks]
            done = sum(1 for t in journey_tasks if t.status == TaskStatus.COMPLETED)
            total_tasks += len(journey_tasks)
            completed_tasks += done
            if journey_tasks and done == len(journey_tasks):
                completed_journeys += 1

        templates = self._admin.list_templates()
        published = sum(1 for t in templates if t.status == TemplateStatus.PUBLISHED)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks else 0.0
        avg_days = (total_days / len(journeys)) if journeys else 0.0

        return AnalyticsResponse(
            total_profiles=len(profiles),
            total_journeys=len(journeys),
            active_journeys=active,
            completed_journeys=completed_journeys,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overall_completion_rate=round(completion_rate, 1),
            total_departments=len(self._admin.list_departments()),
            total_templates=len(templates),
            published_templates=published,
            knowledge_entries=len(self._knowledge.all()),
            average_journey_days=round(avg_days, 1),
        )
