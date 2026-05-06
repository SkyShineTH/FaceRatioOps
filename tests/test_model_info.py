from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_model_info_returns_inference_backend_metadata() -> None:
    response = client.get("/model/info")

    assert response.status_code == 200
    body = response.json()
    assert body["model"]["name"] == "mediapipe-face-mesh"
    assert body["model"]["task"] == "facial_landmark_detection"
