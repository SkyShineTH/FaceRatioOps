from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import routes
from app.inference.landmarks import (
    ImageTooLargeError,
    Landmark,
    LandmarkDetection,
    LandmarkDetectorUnavailable,
)
from app.inference.ratios import (
    FACE_BOTTOM,
    FACE_LEFT,
    FACE_RIGHT,
    FACE_TOP,
    LEFT_EYE_OUTER,
    MOUTH_LEFT,
    MOUTH_RIGHT,
    NOSE_LEFT,
    NOSE_RIGHT,
    RIGHT_EYE_OUTER,
)
from app.main import app

client = TestClient(app)


def _complete_landmarks() -> list[Landmark]:
    points = [Landmark(0.0, 0.0, 0.0) for _ in range(478)]
    points[FACE_LEFT] = Landmark(0.2, 0.5)
    points[FACE_RIGHT] = Landmark(0.8, 0.5)
    points[FACE_TOP] = Landmark(0.5, 0.1)
    points[FACE_BOTTOM] = Landmark(0.5, 0.9)
    points[LEFT_EYE_OUTER] = Landmark(0.35, 0.35)
    points[RIGHT_EYE_OUTER] = Landmark(0.65, 0.35)
    points[NOSE_LEFT] = Landmark(0.45, 0.55)
    points[NOSE_RIGHT] = Landmark(0.55, 0.55)
    points[MOUTH_LEFT] = Landmark(0.4, 0.7)
    points[MOUTH_RIGHT] = Landmark(0.6, 0.7)
    return points


def test_analyze_rejects_unsupported_content_type() -> None:
    response = client.post("/analyze", files={"file": ("face.svg", b"<svg />", "image/svg+xml")})

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported upload type. Upload a JPEG, PNG, or WebP image using multipart field 'file'."
    )


def test_analyze_rejects_empty_image_upload() -> None:
    response = client.post("/analyze", files={"file": ("face.jpg", b"", "image/jpeg")})

    assert response.status_code == 400
    assert response.json()["detail"] == "Image upload is empty. Upload a non-empty JPEG, PNG, or WebP image."


def test_analyze_rejects_upload_above_size_limit(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: SimpleNamespace(max_upload_bytes=8),
    )

    response = client.post("/analyze", files={"file": ("face.jpg", b"x" * 9, "image/jpeg")})

    assert response.status_code == 413
    assert response.json()["detail"] == "Image exceeds the configured upload limit of 8 bytes."


def test_analyze_returns_ratios_for_single_detected_face(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "detect_face_landmarks",
        lambda image_bytes: LandmarkDetection(
            face_detected=True,
            landmarks=_complete_landmarks(),
            confidence=0.98,
            warnings=[],
            model_version="test-double",
        ),
    )

    response = client.post("/analyze", files={"file": ("face.jpg", b"image-bytes", "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert body["face_detected"] is True
    assert body["model"]["name"] == "mediapipe-face-mesh"
    assert body["model"]["version"] == "test-double"
    assert body["ratios"]["face_width_to_height"] == 0.75
    assert body["quality"] == {"warnings": [], "message": None, "confidence": 0.98}


def test_analyze_returns_quality_warning_when_face_not_detected(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "detect_face_landmarks",
        lambda image_bytes: LandmarkDetection(
            face_detected=False,
            landmarks=[],
            confidence=0.0,
            warnings=["face_not_detected"],
            message="No face landmarks were detected. Upload a clear image with exactly one visible face.",
        ),
    )

    response = client.post("/analyze", files={"file": ("face.jpg", b"image-bytes", "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert body["face_detected"] is False
    assert body["ratios"] is None
    assert body["quality"] == {
        "warnings": ["face_not_detected"],
        "message": "No face landmarks were detected. Upload a clear image with exactly one visible face.",
        "confidence": 0.0,
    }


def test_analyze_returns_quality_warning_when_multiple_faces_detected(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "detect_face_landmarks",
        lambda image_bytes: LandmarkDetection(
            face_detected=False,
            landmarks=[],
            confidence=None,
            warnings=["multiple_faces_detected"],
            message="Multiple faces were detected. Upload an image with exactly one visible face.",
        ),
    )

    response = client.post("/analyze", files={"file": ("face.jpg", b"image-bytes", "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert body["face_detected"] is False
    assert body["ratios"] is None
    assert body["quality"] == {
        "warnings": ["multiple_faces_detected"],
        "message": "Multiple faces were detected. Upload an image with exactly one visible face.",
        "confidence": None,
    }


def test_analyze_maps_invalid_images_to_bad_request(monkeypatch) -> None:
    def raise_invalid_image(image_bytes: bytes) -> None:
        raise ValueError("Invalid image upload. Upload a readable JPEG, PNG, or WebP image.")

    monkeypatch.setattr(routes, "detect_face_landmarks", raise_invalid_image)

    response = client.post("/analyze", files={"file": ("face.jpg", b"not-an-image", "image/jpeg")})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image upload. Upload a readable JPEG, PNG, or WebP image."


def test_analyze_maps_decoded_pixel_limit_to_request_entity_too_large(monkeypatch) -> None:
    def raise_too_large(image_bytes: bytes) -> None:
        raise ImageTooLargeError("Image exceeds decoded pixel limit.")

    monkeypatch.setattr(routes, "detect_face_landmarks", raise_too_large)

    response = client.post("/analyze", files={"file": ("face.jpg", b"image-bytes", "image/jpeg")})

    assert response.status_code == 413
    assert response.json()["detail"] == "Image exceeds decoded pixel limit. Configured pixel limit is 12000000 pixels."


def test_analyze_maps_missing_inference_backend_to_service_unavailable(monkeypatch) -> None:
    def raise_unavailable(image_bytes: bytes) -> None:
        raise LandmarkDetectorUnavailable("mediapipe is not installed")

    monkeypatch.setattr(routes, "detect_face_landmarks", raise_unavailable)

    response = client.post("/analyze", files={"file": ("face.jpg", b"image-bytes", "image/jpeg")})

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Face landmark inference backend is unavailable. Install MediaPipe with "
        '`python -m pip install -e ".[inference]"` or run the Docker image.'
    )
