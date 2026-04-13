from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoints() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
