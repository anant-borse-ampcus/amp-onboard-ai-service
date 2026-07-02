"""Tests for authentication, authorization, and security utilities."""

import pytest
from httpx import AsyncClient

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.repositories.seed_data import DEMO_PROFILE_ID


def test_password_hash_and_verify():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_round_trip():
    token = create_access_token(subject="user-1", role="manager")
    claims = decode_access_token(token)
    assert claims["sub"] == "user-1"
    assert claims["role"] == "manager"


@pytest.mark.asyncio
async def test_login_with_seeded_manager(anon_client: AsyncClient):
    response = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "manager"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(anon_client: AsyncClient):
    response = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_and_me(anon_client: AsyncClient):
    register = await anon_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "password123",
            "role": "employee",
        },
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    me = await anon_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_protected_route_requires_auth(anon_client: AsyncClient):
    response = await anon_client.get("/api/v1/profiles")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_manager_only_route_forbidden_for_employee(
    anon_client: AsyncClient, employee_headers: dict
):
    response = await anon_client.get("/api/v1/profiles", headers=employee_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_employee_can_read_own_journey(
    anon_client: AsyncClient, employee_headers: dict
):
    response = await anon_client.get(
        f"/api/v1/journeys/profile/{DEMO_PROFILE_ID}", headers=employee_headers
    )
    assert response.status_code == 200
