from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image

from app.core.config import get_settings


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float
    z: float = 0.0


@dataclass(frozen=True)
class LandmarkDetection:
    face_detected: bool
    landmarks: list[Landmark]
    confidence: float | None
    warnings: list[str]
    model_name: str = "mediapipe-face-mesh"
    model_version: str = "optional-runtime"


class LandmarkDetectorUnavailable(RuntimeError):
    """Raised when the optional MediaPipe inference backend is not installed."""


class ImageTooLargeError(ValueError):
    """Raised when decoded image dimensions exceed the configured safety limit."""


def _load_rgb_image(image_bytes: bytes) -> np.ndarray:
    settings = get_settings()
    Image.MAX_IMAGE_PIXELS = settings.max_image_pixels

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            if width * height > settings.max_image_pixels:
                raise ImageTooLargeError("Image exceeds decoded pixel limit.")
            image.load()
            return np.asarray(image.convert("RGB"))
    except ImageTooLargeError:
        raise
    except (OSError, ValueError) as exc:
        raise ValueError("Invalid image upload.") from exc


def detect_face_landmarks(image_bytes: bytes) -> LandmarkDetection:
    settings = get_settings()
    image = _load_rgb_image(image_bytes)

    try:
        import mediapipe as mp
    except ImportError as exc:
        raise LandmarkDetectorUnavailable("mediapipe is not installed") from exc

    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=settings.max_detected_faces,
        refine_landmarks=True,
        min_detection_confidence=settings.min_detection_confidence,
    ) as face_mesh:
        result = face_mesh.process(image)

    faces = result.multi_face_landmarks or []
    if not faces:
        return LandmarkDetection(
            face_detected=False,
            landmarks=[],
            confidence=0.0,
            warnings=["face_not_detected"],
        )

    if len(faces) > 1:
        return LandmarkDetection(
            face_detected=False,
            landmarks=[],
            confidence=None,
            warnings=["multiple_faces_detected"],
        )

    landmarks = [Landmark(point.x, point.y, point.z) for point in faces[0].landmark]
    return LandmarkDetection(
        face_detected=True,
        landmarks=landmarks,
        confidence=1.0,
        warnings=[],
    )
