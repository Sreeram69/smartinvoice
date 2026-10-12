from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.item_parser import parse_spoken_item

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


def test_parse_spoken_item_direct():
    res1 = parse_spoken_item("boxes count 10 price 2500")
    assert res1["name"].lower() == "boxes"
    assert res1["count"] == "10"
    assert res1["price"] == "2500"

    res2 = parse_spoken_item("add 5 chairs for 1200")
    assert "chairs" in res2["name"].lower()
    assert res2["count"] == "5"
    assert res2["price"] == "1200"

    res3 = parse_spoken_item("item laptop count 2 price 75000")
    assert "laptop" in res3["name"].lower()
    assert res3["count"] == "2"
    assert res3["price"] == "75000"


def test_parse_speech_requires_auth():
    payload = {"speech_text": "boxes count 10 price 2500"}
    response = client.post("/api/v1/items/parse-speech", json=payload)
    assert response.status_code == 401


def test_parse_speech_api_endpoint():
    payload = {"speech_text": "boxes count 10 price 2500"}
    response = client.post("/api/v1/items/parse-speech", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["name"].lower() == "boxes"
    assert data["count"] == "10"
    assert data["price"] == "2500"
