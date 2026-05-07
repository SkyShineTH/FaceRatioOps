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
from app.inference.visualization import calculate_visualization_overlay


def _landmarks() -> list[Landmark]:
    points = [Landmark(0.5, 0.5, 0.0) for _ in range(478)]
    points[0] = Landmark(-0.1, 1.2)
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


def test_calculate_visualization_overlay_from_landmarks() -> None:
    overlay = calculate_visualization_overlay(_landmarks())

    assert overlay is not None
    assert overlay.bounding_box.x_min == 0.0
    assert overlay.bounding_box.y_min == 0.1
    assert overlay.bounding_box.x_max == 0.8
    assert overlay.bounding_box.y_max == 1.0
    assert [segment.name for segment in overlay.measurement_segments] == [
        "face_width",
        "face_top_to_chin",
        "eye_distance",
        "nose_width",
        "mouth_width",
    ]
    assert overlay.measurement_segments[0].label == "Face width segment"
    assert overlay.measurement_segments[0].start.x == 0.2
    assert overlay.measurement_segments[0].end.x == 0.8


def test_calculate_visualization_overlay_returns_none_when_landmarks_are_incomplete() -> None:
    assert calculate_visualization_overlay([Landmark(0.0, 0.0)]) is None
