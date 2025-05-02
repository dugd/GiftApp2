import pytest


@pytest.mark.asyncio
async def test_create_recipient(async_client, simple_user_token_headers):
    recipient_data = {
        "name": "Dori",
        "birthday": "2007-07-15",
        "relation": "Friend",
        "preferences": ["Python", "Chicken"],
        "notes": "bla bla bla...",
    }

    response = await async_client.post("/api/v1/recipients/", headers=simple_user_token_headers, json=recipient_data)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["name"] == recipient_data["name"]
    assert data["preferences"] == recipient_data["preferences"]
    assert data["relation"] == recipient_data["relation"]
    assert data["notes"] == recipient_data["notes"]