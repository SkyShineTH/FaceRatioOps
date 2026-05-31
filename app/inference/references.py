"""Classical facial proportion canons used as a neutral geometric reference.

These are historical drawing/anatomy conventions (neoclassical canons: the vertical
"rule of thirds" and the horizontal "rule of fifths"). They are provided for context
only. They are NOT ideals, targets, beauty scores, or norms a face should match.
Empirical anthropometry (Farkas et al., 1985) shows real faces commonly deviate from
these canons, which is exactly why a measured value sitting outside a band is neutral.
"""

from app.inference.schemas import RatioReference, ReferencesResponse

REFERENCE_DISCLAIMER = (
    "Classical drawing canons (rule of thirds / rule of fifths) shown for context only. "
    "They are not ideals, targets, or scores. Real faces commonly differ from these "
    "canons, so a measurement outside a band is a neutral geometric observation."
)

REFERENCE_SOURCES = [
    "Neoclassical facial canons (Renaissance drawing tradition; codified by Powell & Humphreys, "
    "Proportions of the Aesthetic Face, 1984).",
    "Farkas LG et al., Vertical and horizontal proportions of the face in young adult North "
    "American Caucasians, Plast Reconstr Surg, 1985 — documents how real faces deviate from the canons.",
]

# expected = canon center; lower/upper = a tolerance band around it (not a pass/fail threshold).
_REFERENCE_BANDS: list[RatioReference] = [
    RatioReference(
        field="upper_third_ratio",
        canon="Rule of thirds",
        expected=0.333,
        lower=0.30,
        upper=0.37,
        note="Neoclassical canon divides face height into three equal vertical bands.",
    ),
    RatioReference(
        field="middle_third_ratio",
        canon="Rule of thirds",
        expected=0.333,
        lower=0.30,
        upper=0.37,
        note="Neoclassical canon divides face height into three equal vertical bands.",
    ),
    RatioReference(
        field="lower_third_ratio",
        canon="Rule of thirds",
        expected=0.333,
        lower=0.30,
        upper=0.37,
        note="Neoclassical canon divides face height into three equal vertical bands.",
    ),
    RatioReference(
        field="eye_distance_to_face_width",
        canon="Rule of fifths",
        expected=0.60,
        lower=0.55,
        upper=0.66,
        note="Outer-eye span is ~3/5 of face width under the rule of fifths; the exact value "
        "depends on the face-width landmarks chosen here.",
    ),
    RatioReference(
        field="nose_width_to_face_width",
        canon="Rule of fifths",
        expected=0.20,
        lower=0.17,
        upper=0.24,
        note="Nose width approximates one-fifth of face width under the rule of fifths.",
    ),
    RatioReference(
        field="mouth_width_to_face_width",
        canon="Classical convention",
        expected=0.39,
        lower=0.36,
        upper=0.42,
        note="Mouth width is conventionally a little over one-third of face width.",
    ),
]


def get_reference_bands() -> ReferencesResponse:
    return ReferencesResponse(
        references=list(_REFERENCE_BANDS),
        disclaimer=REFERENCE_DISCLAIMER,
        sources=list(REFERENCE_SOURCES),
    )
