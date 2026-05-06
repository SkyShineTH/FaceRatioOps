from math import dist

from app.inference.landmarks import Landmark
from app.inference.schemas import FaceRatios

FACE_LEFT = 234
FACE_RIGHT = 454
FACE_TOP = 10
FACE_BOTTOM = 152
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263
NOSE_LEFT = 49
NOSE_RIGHT = 279
MOUTH_LEFT = 61
MOUTH_RIGHT = 291


def _point(landmarks: list[Landmark], index: int) -> tuple[float, float]:
    landmark = landmarks[index]
    return landmark.x, landmark.y


def _distance(landmarks: list[Landmark], start: int, end: int) -> float:
    return dist(_point(landmarks, start), _point(landmarks, end))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _symmetry_delta(landmarks: list[Landmark], face_width: float) -> float:
    left_face = _point(landmarks, FACE_LEFT)
    right_face = _point(landmarks, FACE_RIGHT)
    center_x = (left_face[0] + right_face[0]) / 2

    pairs = [
        (_point(landmarks, LEFT_EYE_OUTER), _point(landmarks, RIGHT_EYE_OUTER)),
        (_point(landmarks, NOSE_LEFT), _point(landmarks, NOSE_RIGHT)),
        (_point(landmarks, MOUTH_LEFT), _point(landmarks, MOUTH_RIGHT)),
    ]
    deltas = [abs(abs(center_x - left[0]) - abs(right[0] - center_x)) for left, right in pairs]
    return _safe_ratio(sum(deltas) / len(deltas), face_width)


def calculate_face_ratios(landmarks: list[Landmark]) -> FaceRatios | None:
    required_index = max(
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
    if len(landmarks) <= required_index:
        return None

    face_width = _distance(landmarks, FACE_LEFT, FACE_RIGHT)
    face_height = _distance(landmarks, FACE_TOP, FACE_BOTTOM)
    eye_distance = _distance(landmarks, LEFT_EYE_OUTER, RIGHT_EYE_OUTER)
    nose_width = _distance(landmarks, NOSE_LEFT, NOSE_RIGHT)
    mouth_width = _distance(landmarks, MOUTH_LEFT, MOUTH_RIGHT)

    return FaceRatios(
        face_width_to_height=_safe_ratio(face_width, face_height),
        eye_distance_to_face_width=_safe_ratio(eye_distance, face_width),
        nose_width_to_face_width=_safe_ratio(nose_width, face_width),
        mouth_width_to_face_width=_safe_ratio(mouth_width, face_width),
        symmetry_delta=_symmetry_delta(landmarks, face_width),
    )
