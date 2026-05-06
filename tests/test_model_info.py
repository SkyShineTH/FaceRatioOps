from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_model_info_returns_inference_backend_metadata() -> None:
    response = client.get("/model/info")

    assert response.status_code == 200
    body = response.json()
    assert body["model"]["name"] == "mediapipe-face-mesh"
    assert body["model"]["task"] == "facial_landmark_detection"
    assert isinstance(body["inference_enabled"], bool)
    assert body["capabilities"] == ["face_landmark_detection", "geometric_ratio_calculation"]
    assert "no_face_recognition" in body["limitations"]
    assert "no_beauty_or_attractiveness_scoring" in body["limitations"]


def test_model_info_supports_hyphenated_public_route() -> None:
    response = client.get("/model-info")

    assert response.status_code == 200
    body = response.json()
    assert body["model"]["name"] == "mediapipe-face-mesh"
    assert "no_identity_matching" in body["limitations"]
