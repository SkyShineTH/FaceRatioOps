from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from io import BytesIO
from types import ModuleType
from typing import Any

import numpy as np
from PIL import Image, ImageOps

from app.core.config import get_settings

MODEL_NAME = "mediapipe-face-mesh"
MODEL_TASK = "facial_landmark_detection"
MODEL_VERSION_UNAVAILABLE = "not-installed"
NO_FACE_MESSAGE = "No face landmarks were detected. Upload a clear image with exactly one visible face."
MULTIPLE_FACES_MESSAGE = "Multiple faces were detected. Upload an image with exactly one visible face."


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
    message: str | None = None
    model_name: str = MODEL_NAME
    model_version: str = MODEL_VERSION_UNAVAILABLE


class LandmarkDetectorUnavailable(RuntimeError):
    """Raised when the optional MediaPipe inference backend is not installed."""


class ImageTooLargeError(ValueError):
    """Raised when decoded image dimensions exceed the configured safety limit."""


def get_mediapipe_version() -> str:
    try:
        return version("mediapipe")
    except PackageNotFoundError:
        return MODEL_VERSION_UNAVAILABLE


def _import_mediapipe() -> ModuleType:
    try:
        import mediapipe as mp
    except (ImportError, OSError) as exc:
        raise LandmarkDetectorUnavailable("MediaPipe is not installed or could not be loaded.") from exc
    return mp


def _load_rgb_image(image_bytes: bytes) -> np.ndarray:
    settings = get_settings()
    Image.MAX_IMAGE_PIXELS = settings.max_image_pixels

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            if width * height > settings.max_image_pixels:
                raise ImageTooLargeError("Image exceeds decoded pixel limit.")
            image = ImageOps.exif_transpose(image)
            image.load()
            return np.ascontiguousarray(np.asarray(image.convert("RGB")))
    except ImageTooLargeError:
        raise
    except Image.DecompressionBombError as exc:
        raise ImageTooLargeError("Image exceeds decoded pixel limit.") from exc
    except (OSError, ValueError) as exc:
        raise ValueError("Invalid image upload. Upload a readable JPEG, PNG, or WebP image.") from exc


def detect_face_landmarks(image_bytes: bytes) -> LandmarkDetection:
    settings = get_settings()
    image = _load_rgb_image(image_bytes)
    mp = _import_mediapipe()
    model_version = get_mediapipe_version()

    try:
        with mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=settings.max_detected_faces,
            refine_landmarks=True,
            min_detection_confidence=settings.min_detection_confidence,
        ) as face_mesh:
            result: Any = face_mesh.process(image)
    except (AttributeError, RuntimeError, OSError) as exc:
        raise LandmarkDetectorUnavailable("MediaPipe FaceMesh could not be initialized.") from exc

    faces = result.multi_face_landmarks or []
    if not faces:
        return LandmarkDetection(
            face_detected=False,
            landmarks=[],
            confidence=0.0,
            warnings=["face_not_detected"],
            message=NO_FACE_MESSAGE,
            model_version=model_version,
        )

    if len(faces) > 1:
        return LandmarkDetection(
            face_detected=False,
            landmarks=[],
            confidence=None,
            warnings=["multiple_faces_detected"],
            message=MULTIPLE_FACES_MESSAGE,
            model_version=model_version,
        )

    landmarks = [Landmark(point.x, point.y, point.z) for point in faces[0].landmark]
    return LandmarkDetection(
        face_detected=True,
        landmarks=landmarks,
        confidence=None,
        warnings=[],
        model_version=model_version,
    )
