"""In-memory repositories for System Admin configuration and content."""

import json
from pathlib import Path
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.admin import (
    AIConfig,
    CompanyResource,
    Department,
    KnowledgeEntry,
    OnboardingTemplate,
    OrganizationConfig,
    TemplateStatus,
)

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "data" / "faq_knowledge.json"


class KnowledgeRepository:
    """Knowledge base entries, seeded from the bundled JSON file.

    Shared with the FAQ engine so admin edits are reflected in grounded answers.
    """

    def __init__(self, seed_path: Path | None = None) -> None:
        self._store: dict[UUID, KnowledgeEntry] = {}
        self._seed(seed_path or KNOWLEDGE_PATH)

    def _seed(self, path: Path) -> None:
        if not path.exists():
            return
        for item in json.loads(path.read_text(encoding="utf-8")):
            entry = KnowledgeEntry(
                title=item.get("title", ""),
                answer=item.get("answer", ""),
                keywords=item.get("keywords", []),
                url=item.get("url", ""),
                excerpt=item.get("excerpt", ""),
            )
            self._store[entry.id] = entry

    def all(self) -> list[KnowledgeEntry]:
        return list(self._store.values())

    def as_faq_dicts(self) -> list[dict]:
        return [entry.to_faq_dict() for entry in self._store.values()]

    def add(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        self._store[entry.id] = entry
        return entry

    def delete(self, entry_id: UUID) -> bool:
        if entry_id not in self._store:
            raise NotFoundError(message="Knowledge entry not found")
        del self._store[entry_id]
        return True


class AdminRepository:
    """Holds organization config, AI config, templates, departments, resources."""

    def __init__(self) -> None:
        self.organization = OrganizationConfig()
        self.ai_config = AIConfig()
        self._templates: dict[UUID, OnboardingTemplate] = {}
        self._departments: dict[UUID, Department] = {}
        self._resources: dict[UUID, CompanyResource] = {}
        self._seed()

    def _seed(self) -> None:
        for tpl in [
            OnboardingTemplate(
                name="Engineering Onboarding",
                description="Standard 5-day plan for engineers.",
                role="Software Engineer",
                duration_days=5,
                status=TemplateStatus.PUBLISHED,
                tags=["engineering", "default"],
            ),
            OnboardingTemplate(
                name="Sales Ramp-Up",
                description="7-day ramp for sales hires.",
                role="Account Executive",
                duration_days=7,
                status=TemplateStatus.DRAFT,
                tags=["sales"],
            ),
        ]:
            self._templates[tpl.id] = tpl

        for dept in [
            Department(name="Platform Engineering", lead="Morgan Lee", member_count=12),
            Department(name="Payments", lead="Sam Patel", member_count=8),
            Department(name="People Ops", lead="Riya Shah", member_count=5),
        ]:
            self._departments[dept.id] = dept

        for res in [
            CompanyResource(
                title="Employee Handbook",
                url="/docs/handbook",
                category="policy",
                description="Company policies and expectations.",
            ),
            CompanyResource(
                title="Engineering Wiki",
                url="/wiki",
                category="engineering",
                description="Architecture and runbooks.",
            ),
        ]:
            self._resources[res.id] = res

    # Organization
    def update_organization(self, data: dict) -> OrganizationConfig:
        self.organization = self.organization.model_copy(update=data)
        return self.organization

    # AI config
    def update_ai_config(self, data: dict) -> AIConfig:
        self.ai_config = self.ai_config.model_copy(update=data)
        return self.ai_config

    # Templates
    def list_templates(self) -> list[OnboardingTemplate]:
        return list(self._templates.values())

    def create_template(self, template: OnboardingTemplate) -> OnboardingTemplate:
        self._templates[template.id] = template
        return template

    def update_template(self, template_id: UUID, data: dict) -> OnboardingTemplate:
        tpl = self._templates.get(template_id)
        if tpl is None:
            raise NotFoundError(message="Template not found")
        updated = tpl.model_copy(update=data)
        self._templates[template_id] = updated
        return updated

    def delete_template(self, template_id: UUID) -> bool:
        if template_id not in self._templates:
            raise NotFoundError(message="Template not found")
        del self._templates[template_id]
        return True

    # Departments
    def list_departments(self) -> list[Department]:
        return list(self._departments.values())

    def create_department(self, department: Department) -> Department:
        self._departments[department.id] = department
        return department

    def delete_department(self, department_id: UUID) -> bool:
        if department_id not in self._departments:
            raise NotFoundError(message="Department not found")
        del self._departments[department_id]
        return True

    # Resources
    def list_resources(self) -> list[CompanyResource]:
        return list(self._resources.values())

    def create_resource(self, resource: CompanyResource) -> CompanyResource:
        self._resources[resource.id] = resource
        return resource

    def delete_resource(self, resource_id: UUID) -> bool:
        if resource_id not in self._resources:
            raise NotFoundError(message="Resource not found")
        del self._resources[resource_id]
        return True
