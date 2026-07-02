from uuid import UUID

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
from app.services.admin_service import AdminService


class AdminController:
    """Controller for System Admin endpoints."""

    def __init__(self, service: AdminService) -> None:
        self._service = service

    # Organization
    async def get_organization(self) -> OrganizationResponse:
        return self._service.get_organization()

    async def update_organization(
        self, request: OrganizationUpdateRequest
    ) -> OrganizationResponse:
        return self._service.update_organization(request)

    # AI config
    async def get_ai_config(self) -> AIConfigResponse:
        return self._service.get_ai_config()

    async def update_ai_config(self, request: AIConfigUpdateRequest) -> AIConfigResponse:
        return self._service.update_ai_config(request)

    # Templates
    async def list_templates(self) -> list[TemplateResponse]:
        return self._service.list_templates()

    async def create_template(self, request: TemplateCreateRequest) -> TemplateResponse:
        return self._service.create_template(request)

    async def update_template(
        self, template_id: UUID, request: TemplateUpdateRequest
    ) -> TemplateResponse:
        return self._service.update_template(template_id, request)

    async def publish_template(self, template_id: UUID) -> TemplateResponse:
        return self._service.publish_template(template_id)

    async def delete_template(self, template_id: UUID) -> None:
        self._service.delete_template(template_id)

    # Departments
    async def list_departments(self) -> list[DepartmentResponse]:
        return self._service.list_departments()

    async def create_department(
        self, request: DepartmentCreateRequest
    ) -> DepartmentResponse:
        return self._service.create_department(request)

    async def delete_department(self, department_id: UUID) -> None:
        self._service.delete_department(department_id)

    # Resources
    async def list_resources(self) -> list[ResourceResponse]:
        return self._service.list_resources()

    async def create_resource(self, request: ResourceCreateRequest) -> ResourceResponse:
        return self._service.create_resource(request)

    async def delete_resource(self, resource_id: UUID) -> None:
        self._service.delete_resource(resource_id)

    # Knowledge base
    async def list_knowledge(self) -> list[KnowledgeResponse]:
        return self._service.list_knowledge()

    async def create_knowledge(self, request: KnowledgeCreateRequest) -> KnowledgeResponse:
        return self._service.create_knowledge(request)

    async def delete_knowledge(self, entry_id: UUID) -> None:
        self._service.delete_knowledge(entry_id)

    # Analytics
    async def get_analytics(self) -> AnalyticsResponse:
        return await self._service.get_analytics()
