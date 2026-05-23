# Portfolio Evidence Package

Use this package after the public smoke test in `docs/public-production-smoke-test.md` has real passing evidence.

## Production Story

FaceRatioOps should be presented as a privacy-first AI inference and DevOps operations project for facial landmark detection and geometric ratio analysis. The portfolio value is the production operation of a computer vision inference API, not personal scoring.

## Architecture Summary

```text
Browser / curl / API client
        |
        v
DigitalOcean DNS + Caddy HTTPS
        |
        v
Docker Compose API on 127.0.0.1:8000
        |
        v
FastAPI + MediaPipe Face Mesh Adapter
        |
        v
Technical Geometry JSON + Prometheus Metrics + Structured Logs
```

Optional monitoring:

```text
Prometheus -> /metrics
Grafana -> Prometheus datasource + FaceRatioOps dashboard
```

## Evidence To Capture

| Evidence | Source |
| --- | --- |
| Public workbench without personal image content | `https://faceratioops.skyshine.online/` |
| API docs | `https://faceratioops.skyshine.online/docs` |
| Health response | `https://faceratioops.skyshine.online/health` |
| Model info response | `https://faceratioops.skyshine.online/model-info` |
| Metrics response | `https://faceratioops.skyshine.online/metrics` |
| Grafana dashboard | SSH-tunneled Grafana from `docs/monitoring.md` |
| Container status | Droplet terminal or DigitalOcean dashboard with sensitive fields hidden |
| GitHub checks | CI, CodeQL, Dependabot, manual deploy workflow |

## Resume Bullets

Use only after the relevant evidence exists:

- Deployed a privacy-first FastAPI computer vision inference API on DigitalOcean using Docker Compose and Caddy HTTPS, exposing health, model metadata, and Prometheus metrics endpoints.
- Implemented production-style observability with Prometheus and Grafana dashboards for request rate, latency, status/error rate, and service health while keeping uploaded images in memory and out of logs.
- Built CI and operational quality gates with ruff, pytest, Docker image builds, Dependabot, CodeQL, and a manual GitHub Actions deployment workflow with SSH health checks and rollback documentation.

## Public Wording Rules

Use:

- facial landmark detection
- geometric ratio analysis
- technical confidence
- quality warnings
- explainability overlay
- privacy-first inference API
- production-style DevOps/MLOps operations

Avoid:

- face recognition or identity matching
- beauty, attractiveness, or appearance scoring
- age, gender, race, ethnicity, health, or personality prediction
- medical diagnosis
- cosmetic advice
- surgery recommendations
- objective judgment about a person

## Final Portfolio Checklist

- README includes the public URL only after smoke checks pass.
- Screenshots are stored without secrets, logs, private IPs, or face images.
- Monitoring evidence shows operational metrics only.
- GitHub security screenshots do not reveal secrets or private infrastructure.
- Deployment and rollback docs match the actual production commands used.
- Human review has approved safety-sensitive public wording.
