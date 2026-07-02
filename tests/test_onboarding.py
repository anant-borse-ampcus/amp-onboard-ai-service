"""Tests for Phase 1 onboarding API endpoints."""

from uuid import UUID

import pytest
from httpx import AsyncClient

from app.repositories.seed_data import DEMO_PROFILE_ID, DEMO_JOURNEY_ID


@pytest.mark.asyncio
async def test_list_profiles(client: AsyncClient) -> None:
    response = await client.get("/api/v1/profiles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["id"] == str(DEMO_PROFILE_ID) for p in data)


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/profiles/{DEMO_PROFILE_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alex Rivera"
    assert data["role"] == "Software Engineer"


@pytest.mark.asyncio
async def test_create_profile(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/profiles",
        json={
            "name": "Test User",
            "email": "test.user@example.com",
            "role": "Developer",
            "team": "Engineering",
            "experience_level": "junior",
            "skills": ["Python"],
            "learning_style": "hands_on",
            "start_date": "2026-08-01",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test.user@example.com"


@pytest.mark.asyncio
async def test_analyze_profile(client: AsyncClient) -> None:
    response = await client.post(f"/api/v1/profiles/{DEMO_PROFILE_ID}/analyze")
    assert response.status_code == 200
    data = response.json()
    assert "strengths" in data
    assert "summary" in data


@pytest.mark.asyncio
async def test_get_journey(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/journeys/{DEMO_JOURNEY_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["profile_id"] == str(DEMO_PROFILE_ID)
    assert len(data["days"]) == 3


@pytest.mark.asyncio
async def test_generate_journey(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/journeys/generate",
        json={"profile_id": str(DEMO_PROFILE_ID), "total_days": 5},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_days"] == 5
    assert len(data["days"]) == 5


@pytest.mark.asyncio
async def test_mentor_guidance(client: AsyncClient) -> None:
    journey_response = await client.get(f"/api/v1/journeys/{DEMO_JOURNEY_ID}")
    journey = journey_response.json()
    task_id = journey["days"][0]["tasks"][0]["id"]

    response = await client.post(
        "/api/v1/mentor/guidance",
        json={
            "task_id": task_id,
            "profile_id": str(DEMO_PROFILE_ID),
            "journey_id": str(DEMO_JOURNEY_ID),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "purpose" in data
    assert "tips" in data


@pytest.mark.asyncio
async def test_faq_ask(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/faq/ask",
        json={"question": "How do I set up VPN access?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["confidence"] > 0.5


@pytest.mark.asyncio
async def test_faq_fallback(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/faq/ask",
        json={"question": "What is the meaning of life?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fallback"] is True


@pytest.mark.asyncio
async def test_get_progress(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/progress/profile/{DEMO_PROFILE_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "progress_percentage" in data
    assert data["total_tasks"] > 0
