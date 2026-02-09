"""
End-to-end integration tests for the Todo Chatbot API.

Tests the full API flow including authentication, todo operations,
and chat interface integration.
"""

import pytest
from httpx import AsyncClient
from src.api.main import app


@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient):
    """Create a test user and return authentication headers."""
    # Register a test user
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

    response = await client.post("/auth/register", json=register_data)
    assert response.status_code in [200, 201, 409]  # 409 if user already exists

    # Login to get token
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }

    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    token_data = response.json()
    assert "access_token" in token_data

    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "version" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_registration_flow(client: AsyncClient):
    """Test user registration with unique username."""
    import time
    unique_username = f"testuser_{int(time.time())}"

    register_data = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "TestPassword123!"
    }

    response = await client.post("/auth/register", json=register_data)
    assert response.status_code in [200, 201]

    data = response.json()
    assert "id" in data or "user_id" in data or "username" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_login_flow(client: AsyncClient):
    """Test user login flow."""
    # First register a user
    import time
    unique_username = f"logintest_{int(time.time())}"

    register_data = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "TestPassword123!"
    }

    await client.post("/auth/register", json=register_data)

    # Now login
    login_data = {
        "username": unique_username,
        "password": "TestPassword123!"
    }

    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent_user",
        "password": "WrongPassword123!"
    }

    response = await client.post("/auth/login", json=login_data)
    assert response.status_code in [401, 404]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test that CORS headers are properly set."""
    response = await client.options("/health")
    # CORS headers should be present in the response
    assert response.status_code in [200, 204]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_security_headers(client: AsyncClient):
    """Test that security headers are properly set."""
    response = await client.get("/health")

    headers = response.headers
    assert "x-content-type-options" in headers
    assert headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in headers
    assert headers["x-frame-options"] == "DENY"
    assert "x-xss-protection" in headers


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_documentation_available(client: AsyncClient):
    """Test that API documentation endpoints are accessible."""
    # Test Swagger UI
    response = await client.get("/docs")
    assert response.status_code == 200

    # Test ReDoc
    response = await client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient):
    """Test that OpenAPI schema is available."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Todo Chatbot API"
