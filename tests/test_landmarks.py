import sys
from io import BytesIO
from types import SimpleNamespace

import pytest
from PIL import Image, features

from app.inference import landmarks
from app.inference.landmarks import ImageTooLargeError


def _image_bytes(image_format: str, size: tuple[int, int] = (16, 16)) -> bytes:
    image = Image.new("RGB", size, color=(240, 240, 240))
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


def _fake_face(point_count: int = 478) -> SimpleNamespace:
    points = [SimpleNamespace(x=0.1, y=0.2, z=0.0) for _ in range(point_count)]
    return SimpleNamespace(landmark=points)


def _install_fake_mediapipe(monkeypatch: pytest.MonkeyPatch, faces: list[SimpleNamespace]) -> type:
    class FakeFaceMesh:
        init_kwargs: dict | None = None
        processed_shape: tuple[int, ...] | None = None

        def __init__(self, **kwargs) -> None:
            FakeFaceMesh.init_kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def process(self, image):
            FakeFaceMesh.processed_shape = image.shape
            return SimpleNamespace(multi_face_landmarks=faces)

    fake_module = SimpleNamespace(solutions=SimpleNamespace(face_mesh=SimpleNamespace(FaceMesh=FakeFaceMesh)))
    monkeypatch.setitem(sys.modules, "mediapipe", fake_module)
    monkeypatch.setattr(landmarks, "get_mediapipe_version", lambda: "test-mediapipe")
    return FakeFaceMesh


@pytest.mark.parametrize("image_format", ["JPEG", "PNG"])
def test_load_rgb_image_accepts_supported_raster_formats(image_format: str) -> None:
    image = landmarks._load_rgb_image(_image_bytes(image_format))

    assert image.shape == (16, 16, 3)
    assert image.flags.c_contiguous


def test_load_rgb_image_accepts_webp_when_pillow_supports_it() -> None:
    if not features.check("webp"):
        pytest.skip("Pillow WebP support is not available in this environment.")

    image = landmarks._load_rgb_image(_image_bytes("WEBP"))

    assert image.shape == (16, 16, 3)
    assert image.flags.c_contiguous


def test_load_rgb_image_downscales_oversized_images_to_max_dimension() -> None:
    # Below the pixel-bomb limit but larger than the inference dimension -> should downscale.
    image = landmarks._load_rgb_image(_image_bytes("PNG", size=(2048, 1024)))

    height, width, channels = image.shape
    assert max(width, height) == 1024
    assert (width, height) == (1024, 512)
    assert channels == 3
    assert image.flags.c_contiguous


def test_load_rgb_image_rejects_invalid_image_bytes() -> None:
    with pytest.raises(ValueError, match="Upload a readable JPEG, PNG, or WebP image"):
        landmarks._load_rgb_image(b"not-an-image")


def test_load_rgb_image_rejects_decoded_pixel_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(landmarks, "get_settings", lambda: SimpleNamespace(max_image_pixels=1))

    with pytest.raises(ImageTooLargeError, match="decoded pixel limit"):
        landmarks._load_rgb_image(_image_bytes("PNG", size=(2, 2)))


def test_detect_face_landmarks_processes_real_decoded_image_with_mediapipe_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_face_mesh = _install_fake_mediapipe(monkeypatch, [_fake_face()])

    detection = landmarks.detect_face_landmarks(_image_bytes("PNG"))

    assert detection.face_detected is True
    assert len(detection.landmarks) == 478
    assert detection.confidence is None
    assert detection.message is None
    assert detection.model_version == "test-mediapipe"
    assert fake_face_mesh.processed_shape == (16, 16, 3)
    assert fake_face_mesh.init_kwargs == {
        "static_image_mode": True,
        "max_num_faces": 2,
        "refine_landmarks": True,
        "min_detection_confidence": 0.5,
    }


def test_detect_face_landmarks_returns_clear_no_face_message(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_mediapipe(monkeypatch, [])

    detection = landmarks.detect_face_landmarks(_image_bytes("PNG"))

    assert detection.face_detected is False
    assert detection.warnings == ["face_not_detected"]
    assert detection.message == "No face landmarks were detected. Upload a clear image with exactly one visible face."
    assert detection.confidence == 0.0


def test_detect_face_landmarks_returns_clear_multiple_faces_message(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_mediapipe(monkeypatch, [_fake_face(), _fake_face()])

    detection = landmarks.detect_face_landmarks(_image_bytes("PNG"))

    assert detection.face_detected is False
    assert detection.warnings == ["multiple_faces_detected"]
    assert detection.message == "Multiple faces were detected. Upload an image with exactly one visible face."
    assert detection.confidence is None
