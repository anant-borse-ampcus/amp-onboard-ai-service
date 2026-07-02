from fastapi import APIRouter

from app.routers import admin, auth, branding, health, onboarding

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(admin.router)
api_router.include_router(branding.router)

__all__ = ["api_router"]
