import pytest
from fastapi.testclient import TestClient

try:
    from backend.main import app
except ImportError:
    from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Perfect Five API!"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_characters():
    response = client.get("/characters")
    assert response.status_code == 200
    data = response.json()
    assert "characters" in data
    assert "5" in data["characters"]


def test_get_reference_valid():
    response = client.get("/reference/5")
    assert response.status_code == 200
    data = response.json()
    assert data["character"] == "5"
    assert "edge_points" in data
    assert len(data["edge_points"]) > 0


def test_get_reference_invalid():
    response = client.get("/reference/Z")
    assert response.status_code == 400


def test_score_valid():
    points = [{"x": i * 10, "y": i * 10} for i in range(50)]
    response = client.post(
        "/score",
        json={"character": "5", "user_points": points}
    )
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert 0 <= data["score"] <= 100


def test_score_too_few_points():
    response = client.post(
        "/score",
        json={"character": "5", "user_points": [{"x": 0, "y": 0}]}
    )
    assert response.status_code == 400


def test_score_invalid_character():
    points = [{"x": i * 10, "y": i * 10} for i in range(50)]
    response = client.post(
        "/score",
        json={"character": "Z", "user_points": points}
    )
    assert response.status_code == 400
