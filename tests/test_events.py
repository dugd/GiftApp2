import pytest


@pytest.mark.asyncio
async def test_create_event(async_client, simple_user_token_headers):
    event_data = {
        "title": "Dori's birthday",
        "is_global": False,
        "is_repeating": False,
        "type": "BIRTHDAY",
        "start_date": "2026-07-15"
    }

    response = await async_client.post("/api/v1/events/", headers=simple_user_token_headers, json=event_data)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["title"] == event_data["title"]
    assert data["is_global"] == event_data["is_global"]
    assert data["is_repeating"] == event_data["is_repeating"]
    assert data["type"] == event_data["type"]
    assert data["start_date"] == event_data["start_date"]