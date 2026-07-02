import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["repository"] == "connected"
    assert "service" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_openapi_docs_available(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"]
    assert "/health" in schema["paths"]


@pytest.mark.asyncio
async def test_swagger_ui_available(client):
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_redoc_available(client):
    response = await client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_includes_request_id_header(client):
    response = await client.get("/health")
    assert "x-request-id" in response.headers
    assert "x-process-time-ms" in response.headers


@pytest.mark.asyncio
async def test_not_found_returns_error_envelope(client):
    response = await client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_ERROR"
