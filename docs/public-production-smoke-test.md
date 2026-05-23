# Public Production Smoke Test

This document is the evidence template for the first public DigitalOcean deployment. Do not mark the service as publicly deployed in README, portfolio copy, or resume bullets until this checklist has real results.

Target URL:

```text
https://faceratioops.skyshine.online/
```

Last public verification: not yet run.

## Scope

In scope:

- Public DNS resolution for `faceratioops.skyshine.online`.
- HTTPS certificate and Caddy reverse proxy.
- Public `/`, `/docs`, `/health`, `/model-info`, and `/metrics`.
- Droplet-local loopback API checks.
- Recent Caddy and app logs.

Out of scope:

- Face image upload testing with personal photos.
- Any claim about identity, attractiveness, demographics, health, personality, medical condition, cosmetic value, or surgery guidance.

## Commands

Run from the Droplet:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/model-info
curl -fsS http://127.0.0.1:8000/metrics
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=100 api
```

Run from a local machine:

```bash
curl -fsS https://faceratioops.skyshine.online/health
curl -fsS https://faceratioops.skyshine.online/model-info
curl -fsS https://faceratioops.skyshine.online/metrics
curl -fsS -o /dev/null -w "%{http_code}\n" https://faceratioops.skyshine.online/docs
curl -fsS -o /dev/null -w "%{http_code}\n" https://faceratioops.skyshine.online/
```

## Evidence Table

| Check | Expected | Result |
| --- | --- | --- |
| DNS A record | Points to Droplet public IPv4 | Pending |
| HTTPS root | `200` for `/` | Pending |
| Swagger docs | `200` for `/docs` | Pending |
| Health | `status: ok`, `environment: production` | Pending |
| Model info | Technical capabilities and safety limitations only | Pending |
| Metrics | `faceratioops_http_requests_total` and duration sum | Pending |
| Docker port binding | `127.0.0.1:8000->8000/tcp` | Pending |
| App logs | No image payloads or sensitive biometric data | Pending |
| Caddy logs | No secrets or sensitive payloads | Pending |

## Screenshot Checklist

Capture only screenshots that are safe to publish:

- Public workbench at `/` without a personal face image loaded.
- Swagger UI at `/docs`.
- `/health` response.
- `/metrics` response with operational labels only.
- Grafana dashboard from `docs/monitoring.md`.
- DigitalOcean or container status with secrets, private IPs, tokens, billing data, and personal data hidden.

Do not publish screenshots containing uploaded face images, image previews, raw logs with sensitive data, private keys, tokens, `.env.production`, `.env.monitoring`, or private infrastructure details that should not be public.

## Safety Confirmation

Before marking this smoke test complete, confirm:

- Uploaded images are not permanently stored.
- Logs do not contain raw image bytes, base64 image data, uploaded file contents, biometric templates, identity labels, or sensitive personal attributes.
- Public outputs describe only technical landmark detection, geometric ratios, confidence values, quality warnings, and operational metadata.
- Public copy avoids face recognition, identity matching, beauty or attractiveness scoring, demographic prediction, health prediction, personality inference, medical advice, cosmetic advice, and surgery recommendations.
