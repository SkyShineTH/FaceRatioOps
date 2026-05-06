# FaceRatioOps

Privacy-first AI inference platform for facial geometry analysis.

FaceRatioOps analyzes facial landmarks from uploaded images and calculates geometric face ratios through a production-style API. The project is designed as a DevOps + AI portfolio project: the model is important, but the main focus is building a small inference service that can be tested, containerized, documented, and operated reliably.

## What This Project Does

- Accepts an uploaded JPEG, PNG, or WebP face image through a FastAPI endpoint
- Detects facial landmarks using a MediaPipe-based inference adapter
- Calculates geometric ratios such as face width to height and eye distance to face width
- Returns JSON results with model metadata and quality warnings
- Provides health and model info endpoints for operations
- Uses structured JSON logs without logging uploaded image data

## What This Project Does Not Do

FaceRatioOps does not perform face recognition, identity matching, beauty scoring, age prediction, gender prediction, race or ethnicity prediction, personality inference, medical diagnosis, cosmetic advice, or surgery recommendations.

Uploaded images are processed in memory and are not persisted by the API.

## Architecture

```text
Client / Postman / Web UI
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
- Inference: MediaPipe Face Mesh adapter
- Image processing: Pillow, NumPy
- Validation: Pydantic
- Testing: pytest
- Linting: ruff
- Containerization: Docker, Docker Compose
- CI/CD: GitHub Actions

## API Endpoints

```text
GET  /health
GET  /model/info
POST /analyze
```

`POST /analyze` accepts multipart form data with a `file` field. Uploads are bounded by `MAX_UPLOAD_BYTES`, decoded images are bounded by `MAX_IMAGE_PIXELS`, and unsupported or invalid image data is rejected before inference.

## Example Response

```json
{
  "face_detected": true,
  "model": {
    "name": "mediapipe-face-mesh",
    "version": "optional-runtime",
    "task": "facial_landmark_detection"
  },
  "ratios": {
    "face_width_to_height": 0.74,
    "eye_distance_to_face_width": 0.46,
    "nose_width_to_face_width": 0.23,
    "mouth_width_to_face_width": 0.51,
    "symmetry_delta": 0.04
  },
  "quality": {
    "warnings": [],
    "confidence": 1.0
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

Run the API:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
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

## Privacy and Safety Boundaries

- Image bytes are processed in memory only
- Logs include request metadata such as content type and size, but never image payloads
- The API returns geometric measurements only
- Results must not be interpreted as attractiveness, identity, medical, or personality judgments

## Operations Notes

- `/health` returns app name, version, environment, status, and timestamp
- `/model/info` returns inference backend metadata
- `.env.example` documents safe non-secret defaults
- Docker health checks call `/health`
- The Docker Compose service runs without extra Linux capabilities, with a read-only filesystem and `/tmp` mounted as temporary scratch space

## Future Improvements

- Add annotated landmark visualization
- Add Prometheus-style `/metrics`
- Add Kubernetes manifests and Helm chart
- Add Argo CD GitOps deployment documentation
