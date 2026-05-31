import pytest

from app.inference.landmarks import Landmark
from app.inference.ratios import (
    BROW_CENTER,
    FACE_BOTTOM,
    FACE_LEFT,
    FACE_RIGHT,
    FACE_TOP,
    LEFT_EYE_OUTER,
    MOUTH_LEFT,
    MOUTH_RIGHT,
    NOSE_BASE,
    NOSE_LEFT,
    NOSE_RIGHT,
    RIGHT_EYE_OUTER,
)


@pytest.fixture
def complete_landmarks() -> list[Landmark]:
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
    points[BROW_CENTER] = Landmark(0.5, 0.3)
    points[NOSE_BASE] = Landmark(0.5, 0.6)
    return points
