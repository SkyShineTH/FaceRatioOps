import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.inference.landmarks import (
    MODEL_NAME,
    MODEL_TASK,
    MODEL_VERSION_UNAVAILABLE,
    ImageTooLargeError,
    LandmarkDetectorUnavailable,
    detect_face_landmarks,
    get_mediapipe_version,
)
from app.inference.ratios import calculate_face_ratios
from app.inference.schemas import (
    AnalysisResponse,
    ErrorResponse,
    HealthResponse,
    ModelInfo,
    ModelInfoResponse,
    QualityReport,
)

router = APIRouter()
logger = logging.getLogger("faceratioops.api")
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MODEL_CAPABILITIES = ["face_landmark_detection", "geometric_ratio_calculation"]
MODEL_LIMITATIONS = [
    "no_face_recognition",
    "no_identity_matching",
    "no_demographic_prediction",
    "no_beauty_or_attractiveness_scoring",
    "no_medical_or_cosmetic_advice",
]
HTTP_413_CONTENT_TOO_LARGE = 413
UNSUPPORTED_IMAGE_DETAIL = "Unsupported upload type. Upload a JPEG, PNG, or WebP image using multipart field 'file'."
EMPTY_IMAGE_DETAIL = "Image upload is empty. Upload a non-empty JPEG, PNG, or WebP image."
INFERENCE_UNAVAILABLE_DETAIL = (
    "Face landmark inference backend is unavailable. Install MediaPipe with "
    "`python -m pip install -e \".[inference]\"` or run the Docker image."
)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(UTC),
    )


@router.get("/model-info", response_model=ModelInfoResponse)
@router.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    model_version = get_mediapipe_version()
    return ModelInfoResponse(
        model=ModelInfo(
            name=MODEL_NAME,
            version=model_version,
            task=MODEL_TASK,
        ),
        inference_enabled=model_version != MODEL_VERSION_UNAVAILABLE,
        capabilities=MODEL_CAPABILITIES,
        limitations=MODEL_LIMITATIONS,
    )


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)
async def analyze(file: Annotated[UploadFile, File()]) -> AnalysisResponse:
    settings = get_settings()
    request_id = str(uuid4())

    if file.content_type not in SUPPORTED_IMAGE_TYPES:
        logger.info(
            "rejected upload with unsupported content type",
            extra={"_request_id": request_id, "_content_type": file.content_type},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=UNSUPPORTED_IMAGE_DETAIL,
        )

    image_bytes = await file.read(settings.max_upload_bytes + 1)
    size_bytes = len(image_bytes)

    if size_bytes > settings.max_upload_bytes:
        logger.info(
            "rejected upload above size limit",
            extra={"_request_id": request_id, "_size_bytes": size_bytes},
        )
        raise HTTPException(
            status_code=HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Image exceeds the configured upload limit of {settings.max_upload_bytes} bytes.",
        )

    if size_bytes == 0:
        logger.info("rejected empty upload", extra={"_request_id": request_id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMPTY_IMAGE_DETAIL)

    logger.info(
        "received analysis request",
        extra={
            "_request_id": request_id,
            "_content_type": file.content_type,
            "_size_bytes": size_bytes,
        },
    )

    try:
        detection = detect_face_landmarks(image_bytes)
    except LandmarkDetectorUnavailable as exc:
        logger.warning(
            "landmark backend unavailable",
            extra={"_request_id": request_id, "_reason": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=INFERENCE_UNAVAILABLE_DETAIL,
        ) from exc
    except ImageTooLargeError as exc:
        logger.info("decoded image exceeds size limit", extra={"_request_id": request_id})
        raise HTTPException(
            status_code=HTTP_413_CONTENT_TOO_LARGE,
            detail=f"{exc} Configured pixel limit is {settings.max_image_pixels} pixels.",
        ) from exc
    except ValueError as exc:
        logger.info("invalid image upload", extra={"_request_id": request_id, "_reason": str(exc)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    warnings = list(detection.warnings)
    ratios = calculate_face_ratios(detection.landmarks) if detection.landmarks else None
    if ratios is None and detection.face_detected:
        warnings.append("ratio_calculation_unavailable")

    logger.info(
        "completed analysis request",
        extra={
            "_request_id": request_id,
            "_face_detected": detection.face_detected,
            "_landmark_count": len(detection.landmarks),
            "_warning_count": len(warnings),
        },
    )

    return AnalysisResponse(
        face_detected=detection.face_detected,
        model=ModelInfo(name=detection.model_name, version=detection.model_version, task=MODEL_TASK),
        ratios=ratios,
        quality=QualityReport(warnings=warnings, message=detection.message, confidence=detection.confidence),
    )
