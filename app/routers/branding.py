from fastapi import APIRouter, Depends

from app.controllers.admin_controller import AdminController
from app.core.dependencies import get_admin_controller
from app.schemas.admin import PublicBrandingResponse

router = APIRouter(prefix="/api/v1", tags=["Branding"])


@router.get("/branding", response_model=PublicBrandingResponse)
async def get_public_branding(
    controller: AdminController = Depends(get_admin_controller),
) -> PublicBrandingResponse:
    """Public org branding for theming login and app shell (no auth required)."""
    org = await controller.get_organization()
    return PublicBrandingResponse(
        name=org.name,
        description=org.description,
        primary_color=org.primary_color,
        logo_url=org.logo_url,
    )
