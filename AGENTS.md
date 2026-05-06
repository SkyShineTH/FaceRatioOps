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

## Prompt and Workflow Rules

### Bounded Milestone Prompts

Keep agent prompts scoped to one milestone or one bounded review task. Each prompt should define:

- exact deliverable
- files or modules in scope
- files or behavior out of scope
- acceptance criteria
- required verification commands
- expected handoff notes

Do not combine unrelated backend, inference, Docker, CI, and documentation work into one prompt unless the milestone explicitly requires cross-cutting integration.

### Safety and Scope Prompt Baseline

Every implementation or review prompt must preserve these project boundaries:

- no face recognition or identity matching
- no beauty, attractiveness, demographic, health, or personality prediction
- no medical, cosmetic, or surgery advice
- no permanent uploaded image storage
- no logging of image payloads or sensitive biometric data
- no presentation of geometric ratios as objective judgments about a person

Prompts should describe outputs as technical geometry measurements, confidence values, quality warnings, or explainability visualizations only.

### Human Review Gates

Require human review before merging changes that affect:

- inference behavior or landmark/ratio calculation logic
- API response schemas
- image upload, processing, retention, or logging behavior
- safety-sensitive wording in README, docs, UI, or API messages
- deployment, CI/CD, Docker, or production configuration
- public portfolio language

For high-impact changes, the agent should provide a short risk summary and verification evidence before requesting review.

### Verification Checklist for Handoffs

Each agent handoff should include:

- what changed
- what was intentionally left unchanged
- safety constraints checked
- tests, linting, or build commands run
- any commands not run and why
- known risks or follow-up work
- relevant files changed or reviewed

A task is not complete until the handoff confirms that image data is not permanently stored, sensitive payloads are not logged, and outputs avoid identity, attractiveness, demographic, health, personality, medical, or cosmetic claims.

## Public Portfolio Language

Use English for public README, GitHub profile text, and resume bullets.

Public descriptions should position FaceRatioOps as a privacy-first AI inference and DevOps project for facial landmark detection and geometric ratio analysis. Avoid language that implies cosmetic scoring, attractiveness evaluation, diagnosis, identity recognition, or personal judgment.
