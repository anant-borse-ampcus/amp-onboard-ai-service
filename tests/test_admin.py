"""Tests for System Admin endpoints and role-based access."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.repositories.seed_data import DEMO_ADMIN_ID


def _admin_headers() -> dict[str, str]:
    token = create_access_token(subject=str(DEMO_ADMIN_ID), role="system_admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=_admin_headers()
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_admin_login(anon_client: AsyncClient):
    r = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "system_admin"


@pytest.mark.asyncio
async def test_manager_cannot_access_admin(anon_client: AsyncClient, manager_headers: dict):
    r = await anon_client.get("/api/v1/admin/analytics", headers=manager_headers)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_analytics(admin_client: AsyncClient):
    r = await admin_client.get("/api/v1/admin/analytics")
    assert r.status_code == 200
    data = r.json()
    assert "overall_completion_rate" in data
    assert data["total_departments"] >= 1


@pytest.mark.asyncio
async def test_admin_organization_update(admin_client: AsyncClient):
    r = await admin_client.put(
        "/api/v1/admin/organization", json={"name": "New Org Name"}
    )
    assert r.status_code == 200
    assert r.json()["name"] == "New Org Name"


@pytest.mark.asyncio
async def test_admin_templates_crud(admin_client: AsyncClient):
    r = await admin_client.get("/api/v1/admin/templates")
    assert r.status_code == 200
    initial = len(r.json())

    r = await admin_client.post(
        "/api/v1/admin/templates",
        json={"name": "Design Onboarding", "role": "Designer", "duration_days": 4},
    )
    assert r.status_code == 201
    template_id = r.json()["id"]
    assert r.json()["status"] == "draft"

    r = await admin_client.post(f"/api/v1/admin/templates/{template_id}/publish")
    assert r.status_code == 200
    assert r.json()["status"] == "published"

    r = await admin_client.get("/api/v1/admin/templates")
    assert len(r.json()) == initial + 1

    r = await admin_client.delete(f"/api/v1/admin/templates/{template_id}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_admin_ai_config(admin_client: AsyncClient):
    r = await admin_client.put(
        "/api/v1/admin/ai-config", json={"temperature": 0.7, "enabled": True}
    )
    assert r.status_code == 200
    assert r.json()["temperature"] == 0.7


@pytest.mark.asyncio
async def test_admin_knowledge_reflects_in_faq(
    admin_client: AsyncClient, anon_client: AsyncClient, employee_headers: dict
):
    # Add a knowledge entry as admin
    r = await admin_client.post(
        "/api/v1/admin/knowledge",
        json={
            "title": "Parking Policy",
            "answer": "Parking is available in Lot C with your badge.",
            "keywords": ["parking", "lot"],
        },
    )
    assert r.status_code == 201

    # Employee asks a related FAQ question -> grounded answer from new entry
    r = await anon_client.post(
        "/api/v1/faq/ask",
        headers=employee_headers,
        json={"question": "Where is parking available?"},
    )
    assert r.status_code == 200
    assert r.json()["fallback"] is False


@pytest.mark.asyncio
async def test_admin_departments_and_resources(admin_client: AsyncClient):
    r = await admin_client.post(
        "/api/v1/admin/departments", json={"name": "Design", "lead": "Kai"}
    )
    assert r.status_code == 201

    r = await admin_client.post(
        "/api/v1/admin/resources",
        json={"title": "Brand Guidelines", "url": "/brand", "category": "design"},
    )
    assert r.status_code == 201

    r = await admin_client.get("/api/v1/admin/departments")
    assert any(d["name"] == "Design" for d in r.json())
