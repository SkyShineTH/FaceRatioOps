import pytest

from app.inference.landmarks import Landmark
from app.inference.ratios import calculate_face_ratios


def test_calculate_face_ratios_from_landmarks(complete_landmarks: list[Landmark]) -> None:
    ratios = calculate_face_ratios(complete_landmarks)

    assert ratios is not None
    assert ratios.face_width_to_height == pytest.approx(0.75)
    assert ratios.eye_distance_to_face_width == pytest.approx(0.5)
    assert ratios.nose_width_to_face_width == pytest.approx(0.1667)
    assert ratios.mouth_width_to_face_width == pytest.approx(0.3333)
    assert ratios.symmetry_delta == pytest.approx(0.0)


def test_calculate_face_ratios_returns_none_when_landmarks_are_incomplete() -> None:
    assert calculate_face_ratios([Landmark(0.0, 0.0)]) is None
