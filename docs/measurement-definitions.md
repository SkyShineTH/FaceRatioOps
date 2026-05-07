# Measurement Definitions

FaceRatioOps calculates landmark-derived geometric measurements from MediaPipe Face Mesh landmarks. These measurements are intended for technical explainability and API demonstration only.

They are not certified anthropometric measurements, biometric identity signals, medical measurements, cosmetic assessments, beauty scores, attractiveness scores, demographic indicators, health indicators, personality indicators, or recommendations.

## Source Data

The inference adapter uses MediaPipe Face Mesh landmarks. Each landmark has normalized `x` and `y` coordinates relative to the input image dimensions. FaceRatioOps calculates 2D Euclidean distances between selected landmark pairs and then derives simple ratios.

The current implementation uses these landmark indices:

| Name | Index | Use |
| --- | ---: | --- |
| `FACE_LEFT` | `234` | Left side point for face width. |
| `FACE_RIGHT` | `454` | Right side point for face width. |
| `FACE_TOP` | `10` | Top face landmark used for top-to-chin distance. |
| `FACE_BOTTOM` | `152` | Chin landmark used for top-to-chin distance. |
| `LEFT_EYE_OUTER` | `33` | Outer eye point for eye distance. |
| `RIGHT_EYE_OUTER` | `263` | Outer eye point for eye distance. |
| `NOSE_LEFT` | `49` | Left nose point for nose width. |
| `NOSE_RIGHT` | `279` | Right nose point for nose width. |
| `MOUTH_LEFT` | `61` | Left mouth corner for mouth width. |
| `MOUTH_RIGHT` | `291` | Right mouth corner for mouth width. |

These indices are implementation choices for this portfolio project. They should be reviewed before using the project in any production or research context.

## Distance Formula

All distances are calculated in normalized 2D image space:

```text
distance(a, b) = sqrt((a.x - b.x)^2 + (a.y - b.y)^2)
```

Because coordinates are normalized to the image, output values are relative measurements. They are not physical units such as millimeters or centimeters.

## Ratios

| Response field | Formula | Interpretation |
| --- | --- | --- |
| `face_width_to_height` | `distance(FACE_LEFT, FACE_RIGHT) / distance(FACE_TOP, FACE_BOTTOM)` | Relative width compared with the face-top-to-chin segment. |
| `eye_distance_to_face_width` | `distance(LEFT_EYE_OUTER, RIGHT_EYE_OUTER) / face_width` | Relative outer-eye distance compared with face width. |
| `nose_width_to_face_width` | `distance(NOSE_LEFT, NOSE_RIGHT) / face_width` | Relative nose landmark width compared with face width. |
| `mouth_width_to_face_width` | `distance(MOUTH_LEFT, MOUTH_RIGHT) / face_width` | Relative mouth landmark width compared with face width. |
| `symmetry_delta` | Mean horizontal landmark-pair offset difference divided by face width | Technical left/right landmark displacement proxy. |

`symmetry_delta` is not a beauty, attractiveness, health, or diagnostic score. It is a small geometric proxy derived from selected landmark pairs and should be treated as approximate technical output only.

## Explainability Overlay

The `visualization` response field contains normalized overlay geometry:

- `bounding_box`: min/max normalized `x` and `y` values across detected landmarks.
- `measurement_segments`: selected landmark-to-landmark line segments used to explain the measurements visually.

Current segment names:

| Segment | Landmarks |
| --- | --- |
| `face_width` | `FACE_LEFT` to `FACE_RIGHT` |
| `face_top_to_chin` | `FACE_TOP` to `FACE_BOTTOM` |
| `eye_distance` | `LEFT_EYE_OUTER` to `RIGHT_EYE_OUTER` |
| `nose_width` | `NOSE_LEFT` to `NOSE_RIGHT` |
| `mouth_width` | `MOUTH_LEFT` to `MOUTH_RIGHT` |

The overlay does not detect a true hairline or neck. The vertical segment is labeled `face_top_to_chin` because it uses face landmarks, not hair or neck landmarks.

## Limitations

Measurements can be affected by:

- head pose
- camera angle
- focal length and lens distortion
- lighting
- occlusion
- expression
- image resolution
- cropped or partial faces
- MediaPipe landmark confidence and model behavior

The current implementation does not perform camera calibration, 3D metric reconstruction, demographic normalization, population comparison, or validated anthropometric measurement.

## Safety Boundaries

Do not use or describe these measurements as:

- face recognition or identity matching
- identity verification or authentication
- attractiveness, beauty, or ideal-ratio scoring
- medical diagnosis or health screening
- cosmetic advice or surgery recommendation
- age, gender, race, ethnicity, or personality prediction
- objective judgment about a person

Acceptable wording:

```text
Landmark-derived geometric measurements for technical explainability.
```

Unacceptable wording:

```text
Certified facial proportion score.
Beauty score.
Ideal face ratio.
Diagnostic facial assessment.
```
