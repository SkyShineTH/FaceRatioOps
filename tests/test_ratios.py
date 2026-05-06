import pytest

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
    calculate_face_ratios,
)


def _landmarks() -> list[Landmark]:
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


def test_calculate_face_ratios_from_landmarks() -> None:
    ratios = calculate_face_ratios(_landmarks())

    assert ratios is not None
    assert ratios.face_width_to_height == pytest.approx(0.75)
    assert ratios.eye_distance_to_face_width == pytest.approx(0.5)
    assert ratios.nose_width_to_face_width == pytest.approx(0.1667)
    assert ratios.mouth_width_to_face_width == pytest.approx(0.3333)
    assert ratios.symmetry_delta == pytest.approx(0.0)


def test_calculate_face_ratios_returns_none_when_landmarks_are_incomplete() -> None:
    assert calculate_face_ratios([Landmark(0.0, 0.0)]) is None
