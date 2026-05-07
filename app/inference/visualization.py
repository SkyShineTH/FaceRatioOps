from app.inference.landmarks import Landmark
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
from app.inference.schemas import (
    MeasurementSegment,
    OverlayBoundingBox,
    OverlayPoint,
    VisualizationOverlay,
)

REQUIRED_VISUALIZATION_INDEX = max(
    FACE_LEFT,
    FACE_RIGHT,
    FACE_TOP,
    FACE_BOTTOM,
    LEFT_EYE_OUTER,
    RIGHT_EYE_OUTER,
    NOSE_LEFT,
    NOSE_RIGHT,
    MOUTH_LEFT,
    MOUTH_RIGHT,
)


def calculate_visualization_overlay(landmarks: list[Landmark]) -> VisualizationOverlay | None:
    if len(landmarks) <= REQUIRED_VISUALIZATION_INDEX:
        return None

    return VisualizationOverlay(
        bounding_box=_bounding_box(landmarks),
        measurement_segments=[
            _segment("face_width", "Face width segment", landmarks, FACE_LEFT, FACE_RIGHT),
            _segment("face_top_to_chin", "Face top to chin segment", landmarks, FACE_TOP, FACE_BOTTOM),
            _segment("eye_distance", "Eye distance segment", landmarks, LEFT_EYE_OUTER, RIGHT_EYE_OUTER),
            _segment("nose_width", "Nose width segment", landmarks, NOSE_LEFT, NOSE_RIGHT),
            _segment("mouth_width", "Mouth width segment", landmarks, MOUTH_LEFT, MOUTH_RIGHT),
        ],
    )


def _bounding_box(landmarks: list[Landmark]) -> OverlayBoundingBox:
    x_values = [_clamp(landmark.x) for landmark in landmarks]
    y_values = [_clamp(landmark.y) for landmark in landmarks]
    return OverlayBoundingBox(
        x_min=min(x_values),
        y_min=min(y_values),
        x_max=max(x_values),
        y_max=max(y_values),
    )


def _segment(
    name: str,
    label: str,
    landmarks: list[Landmark],
    start_index: int,
    end_index: int,
) -> MeasurementSegment:
    return MeasurementSegment(
        name=name,
        label=label,
        start=_point(landmarks[start_index]),
        end=_point(landmarks[end_index]),
    )


def _point(landmark: Landmark) -> OverlayPoint:
    return OverlayPoint(x=_clamp(landmark.x), y=_clamp(landmark.y))


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)
