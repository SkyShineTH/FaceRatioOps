import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.inference.landmarks import ImageTooLargeError, LandmarkDetectorUnavailable, detect_face_landmarks
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
HTTP_413_CONTENT_TOO_LARGE = 413


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


@router.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        model=ModelInfo(
            name="mediapipe-face-mesh",
            version="optional-runtime",
            task="facial_landmark_detection",
        )
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
            detail="Only JPEG, PNG, and WebP image uploads are supported.",
        )

    image_bytes = await file.read(settings.max_upload_bytes + 1)
    size_bytes = len(image_bytes)

    if size_bytes > settings.max_upload_bytes:
        logger.info(
            "rejected upload above size limit",
            extra={"_request_id": request_id, "_size_bytes": size_bytes},
        )
        raise HTTPException(status_code=HTTP_413_CONTENT_TOO_LARGE, detail="Image exceeds size limit.")

    if size_bytes == 0:
        logger.info("rejected empty upload", extra={"_request_id": request_id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image upload is empty.")

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
            detail="Face landmark backend is unavailable. Install the inference extras to enable analysis.",
        ) from exc
    except ImageTooLargeError as exc:
        logger.info("decoded image exceeds size limit", extra={"_request_id": request_id})
        raise HTTPException(status_code=HTTP_413_CONTENT_TOO_LARGE, detail=str(exc)) from exc
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
        model=ModelInfo(name=detection.model_name, version=detection.model_version, task="facial_landmark_detection"),
        ratios=ratios,
        quality=QualityReport(warnings=warnings, confidence=detection.confidence),
    )
