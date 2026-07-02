from uuid import UUID

from fastapi import APIRouter, Depends

from app.controllers.admin_controller import AdminController
from app.core.dependencies import get_admin_controller, require_roles
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

# Every admin endpoint requires the system_admin role.
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["System Admin"],
    dependencies=[Depends(require_roles("system_admin"))],
)


# --- Organization / Branding --- #
@router.get("/organization", response_model=OrganizationResponse)
async def get_organization(
    controller: AdminController = Depends(get_admin_controller),
) -> OrganizationResponse:
    return await controller.get_organization()


@router.put("/organization", response_model=OrganizationResponse)
async def update_organization(
    request: OrganizationUpdateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> OrganizationResponse:
    return await controller.update_organization(request)


# --- AI Configuration --- #
@router.get("/ai-config", response_model=AIConfigResponse)
async def get_ai_config(
    controller: AdminController = Depends(get_admin_controller),
) -> AIConfigResponse:
    return await controller.get_ai_config()


@router.put("/ai-config", response_model=AIConfigResponse)
async def update_ai_config(
    request: AIConfigUpdateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> AIConfigResponse:
    return await controller.update_ai_config(request)


# --- Templates --- #
@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(
    controller: AdminController = Depends(get_admin_controller),
) -> list[TemplateResponse]:
    return await controller.list_templates()


@router.post("/templates", response_model=TemplateResponse, status_code=201)
async def create_template(
    request: TemplateCreateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> TemplateResponse:
    return await controller.create_template(request)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    request: TemplateUpdateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> TemplateResponse:
    return await controller.update_template(template_id, request)


@router.post("/templates/{template_id}/publish", response_model=TemplateResponse)
async def publish_template(
    template_id: UUID,
    controller: AdminController = Depends(get_admin_controller),
) -> TemplateResponse:
    return await controller.publish_template(template_id)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    controller: AdminController = Depends(get_admin_controller),
) -> None:
    await controller.delete_template(template_id)


# --- Departments --- #
@router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(
    controller: AdminController = Depends(get_admin_controller),
) -> list[DepartmentResponse]:
    return await controller.list_departments()


@router.post("/departments", response_model=DepartmentResponse, status_code=201)
async def create_department(
    request: DepartmentCreateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> DepartmentResponse:
    return await controller.create_department(request)


@router.delete("/departments/{department_id}", status_code=204)
async def delete_department(
    department_id: UUID,
    controller: AdminController = Depends(get_admin_controller),
) -> None:
    await controller.delete_department(department_id)


# --- Company Resources --- #
@router.get("/resources", response_model=list[ResourceResponse])
async def list_resources(
    controller: AdminController = Depends(get_admin_controller),
) -> list[ResourceResponse]:
    return await controller.list_resources()


@router.post("/resources", response_model=ResourceResponse, status_code=201)
async def create_resource(
    request: ResourceCreateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> ResourceResponse:
    return await controller.create_resource(request)


@router.delete("/resources/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: UUID,
    controller: AdminController = Depends(get_admin_controller),
) -> None:
    await controller.delete_resource(resource_id)


# --- Knowledge Base --- #
@router.get("/knowledge", response_model=list[KnowledgeResponse])
async def list_knowledge(
    controller: AdminController = Depends(get_admin_controller),
) -> list[KnowledgeResponse]:
    return await controller.list_knowledge()


@router.post("/knowledge", response_model=KnowledgeResponse, status_code=201)
async def create_knowledge(
    request: KnowledgeCreateRequest,
    controller: AdminController = Depends(get_admin_controller),
) -> KnowledgeResponse:
    return await controller.create_knowledge(request)


@router.delete("/knowledge/{entry_id}", status_code=204)
async def delete_knowledge(
    entry_id: UUID,
    controller: AdminController = Depends(get_admin_controller),
) -> None:
    await controller.delete_knowledge(entry_id)


# --- Analytics --- #
@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    controller: AdminController = Depends(get_admin_controller),
) -> AnalyticsResponse:
    return await controller.get_analytics()
