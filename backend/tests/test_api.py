from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_start_interview_contract() -> None:
    response = client.post(
        "/api/interview",
        json={
            "sessionId": "test-session",
            "candidate": {"member": {"name": "Test Candidate"}},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["reply"], str)
    assert body["done"] is False
    assert body["feedback"] is None
