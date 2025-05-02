import pytest

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword",
    })

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["role"] == "USER"


@pytest.mark.asyncio
async def test_login_user(async_client):
    await async_client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "securepassword",
    })
    response = await async_client.post("/api/v1/auth/login", data={
        "username": "login@example.com",
        "password": "securepassword",
    })

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token(async_client):
    await async_client.post("/api/v1/auth/register", json={
        "email": "refresh@example.com",
        "password": "securepassword",
    })
    login_resp = await async_client.post("/api/v1/auth/login", data={
        "username": "refresh@example.com",
        "password": "securepassword",
    })
    refresh_token = login_resp.json()["refresh_token"]
    response = await async_client.post("api/v1/auth/refresh", headers={
        "Authorization": f"Bearer {refresh_token}",
    })

    assert response.status_code == 200

    tokens = response.json()

    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_get_current_user(async_client, simple_user_token_headers):
    response = await async_client.get("/api/v1/auth/me", headers=simple_user_token_headers)

    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "user@example.com"
    assert user["role"] == "USER"