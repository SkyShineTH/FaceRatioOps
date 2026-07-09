# FaceRatioOps Operations Runbook

FaceRatioOps is a privacy-first AI inference API for facial landmark detection and geometric ratio analysis. This runbook covers local operation, Docker operation, health checks, metrics, logging, privacy controls, and troubleshooting.

The service must not be operated or described as face recognition, identity matching, beauty scoring, demographic prediction, medical diagnosis, cosmetic advice, surgery recommendation, or personality inference.

## Service Surface

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Readiness check with app name, version, environment, status, and timestamp. |
| `GET /model-info` | Model metadata, inference availability, capabilities, and safety limitations. |
| `GET /model/info` | Compatibility alias for `/model-info`. |
| `GET /metrics` | Prometheus-style request counters and duration sums. |
| `POST /analyze` | Multipart image analysis for facial landmarks, technical geometric ratios, and explainability overlay geometry. |
| `GET /` | Static workbench for local upload preview, `/analyze` submission, and result inspection. |

`POST /analyze` accepts a multipart field named `file` with JPEG, PNG, or WebP content. Uploaded images are read in memory, validated for upload size and decoded pixel count, and are not permanently stored by the API.

The static workbench displays technical facial geometry only. UI copy and displayed outputs must not frame ratios as judgments, recommendations, diagnoses, identity signals, demographic traits, health traits, personality traits, beauty scores, or cosmetic guidance.

`visualization` data contains normalized `0..1` coordinates for `bounding_box` and `measurement_segments`. It is landmark-derived overlay geometry for visual explanation, not an identity region, rating, recommendation, diagnosis, or personal evaluation.

The overlay does not claim to detect a true hairline or neck. The vertical measurement segment uses detected face landmarks and is labeled as `face_top_to_chin`.

Measurement formulas, landmark indices, and limitations are documented in `docs/measurement-definitions.md`.

## Environment Variables

The default non-secret configuration is documented in `.env.example`.

| Variable | Default | Operational use |
| --- | --- | --- |
| `APP_NAME` | `FaceRatioOps` | Service name returned by `/health` and API metadata. |
| `APP_VERSION` | `0.2.0` | Version returned by `/health` and OpenAPI metadata. |
| `ENVIRONMENT` | `development` | Environment label returned by `/health`. |
| `LOG_LEVEL` | `INFO` | Root logging level. |
| `MAX_UPLOAD_BYTES` | `5242880` | Maximum raw upload size read by `/analyze`. |
| `MAX_IMAGE_PIXELS` | `12000000` | Maximum decoded image pixel count. |
| `MAX_DETECTED_FACES` | `2` | Maximum faces requested from the MediaPipe adapter. |
| `MIN_DETECTION_CONFIDENCE` | `0.5` | Minimum detection confidence passed to MediaPipe. |

These settings are operational controls, not product claims. Raising image or face limits increases CPU and memory risk and should be reviewed before deployment.

## Local Operation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,inference]"
```

Run the API:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Verify operational endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/model-info
Invoke-RestMethod http://127.0.0.1:8000/metrics
```

Open the static workbench:

```text
http://127.0.0.1:8000/
```

Verify image analysis with a local image that contains exactly one visible face:

```powershell
$ImagePath = "C:\path\to\single-face.jpg"
curl.exe -s -F "file=@$ImagePath" http://127.0.0.1:8000/analyze
```

Do not commit real face images or test images that contain people to the repository.

## Docker Operation

Build and run the image:

```powershell
docker build -t faceratioops:local .
docker run --rm -d --name faceratioops-api -p 8000:8000 faceratioops:local
```

Check health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Stop the container:

```powershell
docker stop faceratioops-api
```

Run with Docker Compose:

```powershell
docker compose up --build
```

The Compose service uses a read-only filesystem, drops Linux capabilities, sets `no-new-privileges`, and mounts `/tmp` as temporary scratch space.

Validate the production Compose override:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

The production override uses the prebuilt GHCR image by default and binds the API to `127.0.0.1:8000` so Caddy can proxy it without exposing port `8000` directly to the public internet. On low-memory Droplets, use `docker compose pull` and `up -d --no-build`; do not build MediaPipe dependencies on the server.

For the latest local production Compose smoke-test evidence, see `docs/local-production-smoke-test.md`.

## Deployment Readiness

The service was deployed on DigitalOcean behind HTTPS. The live environment was decommissioned on 2026-07-09. The deployment runbook is preserved in `docs/digitalocean-deployment.md` and the full stack is defined in Git.

Former public URLs (no longer live):

```text
https://faceratioops.skyshine.online/
```

Expected public operational endpoints (offline):

```text
https://faceratioops.skyshine.online/health
https://faceratioops.skyshine.online/docs
https://faceratioops.skyshine.online/model-info
https://faceratioops.skyshine.online/metrics
```

The live environment was deployed using `docs/digitalocean-deployment.md` as the manual deployment runbook. The environment was decommissioned on 2026-07-09 and can be redeployed from Git.

Before exposing the API publicly, confirm:

- `docker-compose.prod.yml` is used with `docker-compose.yml`.
- The default GHCR image is acceptable, or `FACERATIOOPS_IMAGE` is exported in the shell for a specific rollback/test image.
- `deploy/Caddyfile` is installed or copied into the host Caddy config.
- Upload limits are conservative for the Droplet size.
- Image bytes are processed in memory only and are not written to disk.
- Logs do not include image payloads, base64 image data, uploaded file contents, biometric templates, or sensitive personal attributes.
- Public endpoint copy describes technical geometry measurements only.
- Error messages remain technical and do not judge a person's appearance.
- Human review has approved deployment, Docker, CI/CD, and public wording changes.

## Logging

Logs are structured JSON written to stdout. The API logs operational metadata such as request IDs, content type, upload size, detection status, landmark count, warning count, and technical error reasons.

Operators must not add logging for:

- raw image bytes
- base64-encoded image payloads
- uploaded file contents
- persistent biometric templates
- identity labels or recognition results
- attractiveness, demographic, health, personality, medical, cosmetic, or surgery interpretations

Expected safe log examples include:

```json
{"level":"INFO","logger":"faceratioops.api","message":"received analysis request","request_id":"...","content_type":"image/jpeg","size_bytes":123456}
```

## Metrics

`GET /metrics` returns Prometheus-style counters:

- `faceratioops_http_requests_total`
- `faceratioops_http_request_duration_seconds_sum`

Labels include method, route path, and HTTP status. Metrics should be used for service behavior and reliability only. They must not include image contents, user identity, biometric templates, demographic labels, or personal attributes.

The first monitoring milestone is API metrics-first monitoring through the existing `/metrics` endpoint. Optional Prometheus and Grafana configuration is available in `docker-compose.monitoring.yml` and `deploy/`. Start it only after the API is stable, and scrape only operational metrics.

API metrics-first verification:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/model-info
Invoke-RestMethod http://127.0.0.1:8000/metrics
```

Confirm the metrics output includes `faceratioops_http_requests_total` and `faceratioops_http_request_duration_seconds_sum` with only method, path, and status labels.

Start API monitoring with:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.monitoring.yml --profile monitoring up -d --no-build
```

Prometheus and Grafana bind to `127.0.0.1:9090` and `127.0.0.1:3000`. For remote access, use an SSH tunnel instead of exposing those ports publicly. See `docs/monitoring.md`.

## CI/CD And GitHub Verification

The GitHub Actions workflow in `.github/workflows/ci.yml` runs on push and pull request to `main`.

The pipeline verifies:

- Python dependency installation.
- `ruff check .`
- `pytest`
- Docker image build.

Additional repository controls:

- `.github/workflows/publish-image.yml` builds and publishes the GHCR image used by production Compose.
- `.github/workflows/deploy.yml` provides manual-only DigitalOcean deployment through `workflow_dispatch`.
- `.github/workflows/codeql.yml` runs CodeQL analysis for Python.
- `.github/dependabot.yml` configures dependency update PRs.

Before changing deployment, Docker, monitoring, CI, or production configuration, run the closest local equivalent and include the results in the handoff. These changes require human review before merge.

## Privacy And Safety Checks

Before merging operational or deployment changes, verify:

- Uploaded images are processed in memory and are not permanently stored.
- Logs do not include image payloads, base64 image data, biometric templates, or sensitive personal data.
- API outputs describe technical geometry measurements, confidence values, and quality warnings only.
- Visualization overlays describe detected face area and measurement paths only.
- Public wording avoids face recognition, identity matching, beauty scoring, demographic prediction, health prediction, personality inference, medical advice, cosmetic advice, and surgery recommendations.
- Error messages remain technical and do not judge a person's appearance.

Changes that affect inference behavior, API response schemas, image processing or retention, logging, deployment configuration, CI/CD, or public portfolio language require human review before merge.

## Troubleshooting

### MediaPipe is unavailable

Symptom: `/analyze` returns `503 Service Unavailable`.

Check `/model-info`. If `inference_enabled` is `false`, install the inference extra:

```powershell
python -m pip install -e ".[inference]"
```

The Docker image installs the inference extra during build.

### Unsupported upload type

Symptom: `/analyze` returns `400 Bad Request` with an unsupported upload type message.

Use JPEG, PNG, or WebP content and submit the file as multipart field `file`.

### Upload exceeds size limit

Symptom: `/analyze` returns `413`.

Check `MAX_UPLOAD_BYTES` for raw upload size and `MAX_IMAGE_PIXELS` for decoded pixel count. Prefer lowering input image dimensions instead of increasing limits.

### No face or multiple faces detected

Symptom: `/analyze` returns `face_detected: false` with `face_not_detected` or `multiple_faces_detected`.

Use a clear image with exactly one visible face. This is a technical input-quality condition, not a judgment about the person in the image.

## Handoff Checklist

For each operational change, include:

- What changed.
- What was intentionally left unchanged.
- Safety constraints checked.
- Tests, linting, or build commands run.
- Commands not run and why.
- Known risks or follow-up work.
- Files changed or reviewed.

Minimum verification before handoff:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
docker build -t faceratioops:local .
```

If Docker is unavailable locally, document that clearly in the handoff.
