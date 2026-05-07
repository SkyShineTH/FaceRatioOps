from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    timestamp: datetime


class ModelInfo(BaseModel):
    name: str
    version: str
    task: str


class ModelInfoResponse(BaseModel):
    model: ModelInfo
    inference_enabled: bool
    capabilities: list[str]
    limitations: list[str]


class FaceRatios(BaseModel):
    face_width_to_height: float = Field(ge=0)
    eye_distance_to_face_width: float = Field(ge=0)
    nose_width_to_face_width: float = Field(ge=0)
    mouth_width_to_face_width: float = Field(ge=0)
    symmetry_delta: float = Field(ge=0)


class OverlayPoint(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class OverlayBoundingBox(BaseModel):
    x_min: float = Field(ge=0, le=1)
    y_min: float = Field(ge=0, le=1)
    x_max: float = Field(ge=0, le=1)
    y_max: float = Field(ge=0, le=1)


class MeasurementSegment(BaseModel):
    name: str
    label: str
    start: OverlayPoint
    end: OverlayPoint


class VisualizationOverlay(BaseModel):
    bounding_box: OverlayBoundingBox
    measurement_segments: list[MeasurementSegment]


class QualityReport(BaseModel):
    warnings: list[str]
    message: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class AnalysisResponse(BaseModel):
    face_detected: bool
    model: ModelInfo
    ratios: FaceRatios | None
    visualization: VisualizationOverlay | None = None
    quality: QualityReport


class ErrorResponse(BaseModel):
    detail: str
