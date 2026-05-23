# DigitalOcean Manual Deployment Runbook

This runbook prepares FaceRatioOps for a manual DigitalOcean deployment using Docker Compose and Caddy HTTPS. It is a docs-only deployment plan: it does not mean the service is already deployed.

The target public URL is:

```text
https://faceratioops.skyshine.online/
```

Expected operational endpoints:

```text
https://faceratioops.skyshine.online/health
https://faceratioops.skyshine.online/docs
https://faceratioops.skyshine.online/model-info
https://faceratioops.skyshine.online/metrics
```

Do not operate or describe the service as face recognition, identity matching, beauty scoring, demographic prediction, health inference, personality inference, medical advice, cosmetic advice, or surgery recommendation.

## Deployment Design

```text
Browser / curl / API client
        |
        v
DigitalOcean DNS
        |
        v
Caddy HTTPS reverse proxy
        |
        v
Docker Compose service on 127.0.0.1:8000
        |
        v
FastAPI + MediaPipe Face Mesh adapter
```

Default host-level choices:

- Droplet: small Ubuntu LTS Droplet with enough memory for MediaPipe inference.
- DNS: `A` record for `faceratioops.skyshine.online` pointing to the Droplet public IPv4 address.
- HTTPS: host-installed Caddy using `deploy/Caddyfile` and proxying to `127.0.0.1:8000`.
- App runtime: `docker-compose.yml` plus `docker-compose.prod.yml`.
- Deployment trigger: manual SSH commands for the first production-style deployment.

The repository's base Compose port mapping is intended for local development. The production override maps `127.0.0.1:8000:8000`; use it for public deployments so the API is reachable only through Caddy. Do not expose container port `8000` directly to the public internet.

## Pre-Deployment Checklist

- Confirm the repository is clean or all intended changes are committed.
- Confirm `ruff check .` and `pytest` pass locally or in CI.
- Confirm `docker build -t faceratioops:local .` succeeds.
- Confirm `docker compose -f docker-compose.yml -f docker-compose.prod.yml config` succeeds.
- Confirm `.env.production` is created on the Droplet from `.env.production.example`; do not commit `.env.production`.
- Confirm `ENVIRONMENT=production` is set in `.env.production`.
- Keep `MAX_UPLOAD_BYTES` and `MAX_IMAGE_PIXELS` conservative for the first public deployment.
- Confirm image uploads are processed in memory only and are not persisted by the API.
- Confirm logs contain request metadata only and do not include image payloads or base64 image data.
- Confirm public copy describes technical geometry measurements only.
- Confirm `deploy/Caddyfile` contains the expected public hostname before installing it on the Droplet.

## Droplet Setup

SSH into the Droplet as the deployment user:

```bash
ssh <user>@<droplet-ip>
```

Install Docker, Docker Compose plugin, Git, and Caddy using the package manager approved for the host image. After installation, verify:

```bash
docker --version
docker compose version
caddy version
git --version
```

Open only the required public ports:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## Application Deployment

Clone or update the repository:

```bash
git clone https://github.com/SkyShineTH/FaceRatioOps.git
cd FaceRatioOps
```

For an existing checkout:

```bash
cd FaceRatioOps
git fetch origin
git checkout main
git pull --ff-only origin main
```

Create the runtime environment file:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` on the Droplet:

```text
APP_NAME=FaceRatioOps
APP_VERSION=0.2.0
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_UPLOAD_BYTES=5242880
MAX_IMAGE_PIXELS=12000000
MAX_DETECTED_FACES=2
MIN_DETECTION_CONFIDENCE=0.5
```

Validate the merged production Compose config:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

Confirm the generated `api` service has exactly this public port binding:

```text
127.0.0.1:8000->8000/tcp
```

Start the API:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

Verify from the Droplet:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/model-info
curl -fsS http://127.0.0.1:8000/metrics
```

## Caddy HTTPS Proxy

The repository includes `deploy/Caddyfile`:

```caddyfile
faceratioops.skyshine.online {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8000
}
```

Install it on the host after DNS points to the Droplet:

```bash
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
```

Reload Caddy:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager
```

Verify from a local machine:

```bash
curl -fsS https://faceratioops.skyshine.online/health
curl -fsS https://faceratioops.skyshine.online/model-info
curl -fsS https://faceratioops.skyshine.online/metrics
```

Open in a browser:

```text
https://faceratioops.skyshine.online/
https://faceratioops.skyshine.online/docs
```

## API Metrics-First Verification

The first monitoring milestone uses the existing `/metrics` endpoint before adding Prometheus or Grafana.

Generate a small amount of operational traffic:

```bash
curl -fsS https://faceratioops.skyshine.online/health
curl -fsS https://faceratioops.skyshine.online/model-info
curl -fsS https://faceratioops.skyshine.online/docs >/dev/null
curl -fsS https://faceratioops.skyshine.online/metrics
```

Confirm the metrics output includes:

```text
faceratioops_http_requests_total
faceratioops_http_request_duration_seconds_sum
```

Metrics labels must stay limited to HTTP method, route path, and status code. Do not add image data, user identity, biometric templates, demographic labels, or personal attributes as metric labels.

## Logs And Operations

Inspect service logs:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=100 api
```

Expected safe log fields include request ID, content type, upload size, detection status, landmark count, warning count, and technical error reasons.

Logs must not include:

- raw image bytes
- base64 image data
- uploaded file contents
- biometric templates
- identity labels or recognition results
- attractiveness, demographic, health, personality, medical, cosmetic, or surgery interpretations

Restart the service:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart api
```

Stop the service:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

Rollback to the previous commit if needed:

```bash
git log --oneline -5
git checkout <previous-commit>
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
curl -fsS http://127.0.0.1:8000/health
```

After rollback validation, decide whether to stay pinned to the previous commit or return to `main`.

## Portfolio Evidence Checklist

Capture screenshots only after the public endpoint is verified:

- `https://faceratioops.skyshine.online/`
- `https://faceratioops.skyshine.online/docs`
- `https://faceratioops.skyshine.online/health`
- `https://faceratioops.skyshine.online/metrics`
- DigitalOcean Droplet or container status if it does not expose private information.

Do not capture or publish screenshots containing uploaded face images, personal image content, secrets, private IPs that should remain private, or logs with sensitive data.

## Next Milestones

- Review the local production Compose smoke-test evidence in `docs/local-production-smoke-test.md`.
- Complete the public smoke-test evidence in `docs/public-production-smoke-test.md`.
- Start optional Prometheus and Grafana monitoring with `docs/monitoring.md`.
- Capture Grafana dashboard screenshots for request count, latency, errors, and health visibility.
- Configure the manual `workflow_dispatch` deployment and rollback path with `docs/deployment-workflow-and-rollback.md`.
- Enable GitHub security and quality settings with `docs/github-security-quality.md`.
