# Agent context - FaceRatioOps

FaceRatioOps is a privacy-first AI inference platform for facial geometry analysis.

## Project Goal

Build a production-style AI inference API that detects facial landmarks from uploaded images and calculates geometric face ratios.

## Positioning

This is a DevOps + AI portfolio project. The main value is not cosmetic scoring, but reliable deployment of a computer vision inference service.

## Safety Boundaries

The project must not:

- perform face recognition or identity matching
- predict beauty, attractiveness, age, gender, race, ethnicity, health, or personality
- provide medical diagnosis, cosmetic advice, or surgery recommendations
- store uploaded face images permanently
- log image payloads or sensitive biometric data
- present geometric ratios as objective judgments about a person

The project may:

- detect face landmarks
- calculate geometric ratios
- return technical confidence and quality warnings
- visualize landmark points for explainability

## Technical Direction

- Backend: FastAPI
- Inference: MediaPipe Face Landmarker or a practical MediaPipe face mesh implementation
- Data processing: OpenCV and NumPy
- Testing: pytest
- Linting: ruff
- Containerization: Docker and Docker Compose
- CI/CD: GitHub Actions

## DevOps Requirements

The project should include:

- health endpoint
- model info endpoint
- structured logs
- environment variables via `.env.example`
- Dockerfile
- docker-compose.yml
- CI workflow for lint, tests, and Docker build
- production-style README
- operational documentation

## Public Portfolio Language

Use English for public README, GitHub profile text, and resume bullets.
