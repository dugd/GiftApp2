import pytest

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["role"] == "USER"