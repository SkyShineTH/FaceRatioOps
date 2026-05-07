# FaceRatioOps

Privacy-first AI inference platform for facial geometry analysis.

FaceRatioOps analyzes facial landmarks from uploaded images and calculates geometric face ratios through a production-style API. The project is designed as a DevOps + AI portfolio project: the model is important, but the main focus is building a small inference service that can be tested, containerized, documented, and operated reliably.

## What This Project Does

- Accepts an uploaded JPEG, PNG, or WebP face image through a FastAPI endpoint
- Detects facial landmarks using a MediaPipe-based inference adapter
- Calculates geometric ratios such as face width to height and eye distance to face width
- Returns landmark-derived visualization geometry for explainability overlays
- Returns JSON results with model metadata and quality warnings
- Provides health and model info endpoints for operations
- Uses structured JSON logs without logging uploaded image data

## What This Project Does Not Do

FaceRatioOps does not perform face recognition, identity matching, beauty scoring, age prediction, gender prediction, race or ethnicity prediction, personality inference, medical diagnosis, cosmetic advice, or surgery recommendations.

Uploaded images are processed in memory and are not persisted by the API.

The explainability overlay uses MediaPipe face landmarks. It does not detect a true hairline or neck landmark; the vertical measurement path is labeled as a face-top-to-chin segment.

See [docs/measurement-definitions.md](docs/measurement-definitions.md) for landmark indices, formulas, overlay definitions, and limitations.

## Architecture

```text
Client / Postman / curl
        |
        v
FastAPI Inference API
        |
        v
MediaPipe Face Landmark Adapter
        |
        v
Ratio Calculator
        |
        v
JSON Response + Structured Logs + Health Checks
```

## Tech Stack

- Backend: FastAPI
- Inference: MediaPipe Face Mesh adapter through the `inference` extra
- Image processing: Pillow, NumPy
- Validation: Pydantic
- Testing: pytest
- Linting: ruff
- Containerization: Docker, Docker Compose
- CI/CD: GitHub Actions

## API Endpoints

```text
GET  /health
GET  /model-info
GET  /model/info
GET  /metrics
POST /analyze
```

`POST /analyze` accepts multipart form data with a `file` field. Uploads are bounded by `MAX_UPLOAD_BYTES`, decoded images are bounded by `MAX_IMAGE_PIXELS`, and unsupported or invalid image data is rejected before inference.

## Example Response

```json
{
  "face_detected": true,
  "model": {
    "name": "mediapipe-face-mesh",
    "version": "0.10.x",
    "task": "facial_landmark_detection"
  },
  "ratios": {
    "face_width_to_height": 0.74,
    "eye_distance_to_face_width": 0.46,
    "nose_width_to_face_width": 0.23,
    "mouth_width_to_face_width": 0.51,
    "symmetry_delta": 0.04
  },
  "visualization": {
    "bounding_box": {
      "x_min": 0.21,
      "y_min": 0.12,
      "x_max": 0.78,
      "y_max": 0.91
    },
    "measurement_segments": [
      {
        "name": "face_width",
        "label": "Face width segment",
        "start": {"x": 0.21, "y": 0.5},
        "end": {"x": 0.78, "y": 0.5}
      }
    ]
  },
  "quality": {
    "warnings": [],
    "message": null,
    "confidence": null
  }
}
```

## Local Development

Create a virtual environment and install development dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Install the optional MediaPipe inference backend when you want `/analyze` to process real images:

```powershell
python -m pip install -e ".[inference]"
```

The `inference` extra pins a MediaPipe release that includes the `mp.solutions.face_mesh` API used by this adapter.

For one local environment with both development tools and real-image inference:

```powershell
python -m pip install -e ".[dev,inference]"
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

The static workbench is available at:

```text
http://127.0.0.1:8000/
```

It lets you choose a local image, preview it in the browser, submit it to `/analyze`, and inspect technical geometry results with an explainability overlay without adding a separate frontend service.

## Manual Real-Image Verification

Use a local JPEG, PNG, or WebP image with exactly one visible face. Do not commit real face images to the repository.

Run the API locally with MediaPipe installed:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,inference]"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, call the operational endpoints and `/analyze`:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/model-info
$ImagePath = "C:\path\to\single-face.jpg"
curl.exe -s -F "file=@$ImagePath" http://127.0.0.1:8000/analyze
```

Expected technical outcomes:

- A readable image with exactly one visible face returns `face_detected: true`, MediaPipe model metadata, geometric ratios, and no judgmental scoring.
- A readable image with no detectable face returns `face_detected: false`, `face_not_detected`, and a technical quality message.
- A readable image with multiple visible faces returns `face_detected: false`, `multiple_faces_detected`, and a message asking for exactly one visible face.
- Unsupported, invalid, empty, or oversized uploads return clear 400 or 413 error details.

Equivalent Docker flow:

```powershell
docker build -t faceratioops:local .
docker run --rm -d --name faceratioops-api -p 8000:8000 faceratioops:local
Invoke-RestMethod http://127.0.0.1:8000/health
$ImagePath = "C:\path\to\single-face.jpg"
curl.exe -s -F "file=@$ImagePath" http://127.0.0.1:8000/analyze
docker stop faceratioops-api
```

## Docker Workflow

Build and run locally:

```powershell
docker build -t faceratioops:local .
docker compose up --build
```

The container exposes the API on:

```text
http://127.0.0.1:8000
```

## CI/CD Pipeline

The GitHub Actions workflow runs on push and pull request to `main`:

- install Python dependencies
- run `ruff check .`
- run `pytest`
- build the Docker image

Unit tests are deterministic and do not require real face images or MediaPipe downloads. The inference adapter tests use generated in-memory raster images and a fake MediaPipe module to verify the adapter contract.

## Privacy and Safety Boundaries

- Image bytes are processed in memory only
- Logs include request metadata such as content type and size, but never image payloads
- The API returns geometric measurements only
- Visualization overlays show landmark-derived technical measurement paths only
- Results must not be interpreted as attractiveness, identity, medical, or personality judgments
- Measurement definitions and limitations are documented in [docs/measurement-definitions.md](docs/measurement-definitions.md)

## Operations Notes

- `/health` returns app name, version, environment, status, and timestamp
- `/model-info` returns inference backend metadata, technical capabilities, and safety limitations
- `/model/info` remains available as a compatibility route
- `/metrics` exposes Prometheus-style request counters and request duration sums
- `.env.example` documents safe non-secret defaults
- Docker health checks call `/health`
- The Docker Compose service runs without extra Linux capabilities, with a read-only filesystem and `/tmp` mounted as temporary scratch space
- See [docs/operations.md](docs/operations.md) for the local runbook, Docker workflow, logging guidance, privacy checks, and troubleshooting notes

## Future Improvements

- Add Kubernetes manifests and Helm chart
- Add Argo CD GitOps deployment documentation
