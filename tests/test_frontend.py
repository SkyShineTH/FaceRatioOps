from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_frontend_workbench_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "FaceRatioOps" in response.text
    assert "attractiveness" in response.text
    assert "does not perform identity matching" in response.text
