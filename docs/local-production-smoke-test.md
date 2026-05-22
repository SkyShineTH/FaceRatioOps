# Local Production Smoke Test

This smoke test verifies the production Compose override before a public DigitalOcean deployment. It confirms that the API starts with production environment values, binds only to loopback on the host, exposes the expected operational endpoints, and does not log uploaded image payloads.

Last local verification: 2026-05-23 Asia/Bangkok.

## Scope

In scope:

- Merged `docker-compose.yml` and `docker-compose.prod.yml` configuration.
- Local container startup using the production override.
- `/health`, `/model-info`, `/docs`, and `/metrics`.
- Container health status, loopback port binding, and recent API logs.

Out of scope:

- Public DNS, HTTPS, and Caddy certificate issuance.
- DigitalOcean firewall configuration.
- Automated CI/CD deployment.
- Image analysis upload testing with personal face images.

## Commands

Validate the merged production Compose configuration:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

Start the stack:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Check container status and host port binding:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

Smoke the operational endpoints:

```powershell
curl.exe -fsS http://127.0.0.1:8000/health
curl.exe -fsS http://127.0.0.1:8000/model-info
curl.exe -fsS -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/docs
curl.exe -fsS http://127.0.0.1:8000/metrics
```

Review recent logs:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=100 api
```

Stop the local stack after verification:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

## Verification Evidence

The 2026-05-23 local smoke test produced these results:

- Merged Compose config succeeded and mapped the API as `127.0.0.1:8000:8000`.
- Container status was `healthy`.
- `docker compose ps` showed `127.0.0.1:8000->8000/tcp`.
- `/health` returned `status: ok`, `app: FaceRatioOps`, `version: 0.2.0`, and `environment: production`.
- `/model-info` returned `inference_enabled: true` with facial landmark detection and geometric ratio calculation capabilities.
- `/docs` returned HTTP `200`.
- `/metrics` exposed `faceratioops_http_requests_total` and `faceratioops_http_request_duration_seconds_sum` for the smoke-test requests.
- Recent container logs contained request method, path, and status metadata for `/health`, `/model-info`, `/docs`, and `/metrics`.

## Safety Checks

- No image upload was performed during this smoke test.
- No uploaded image bytes, base64 image data, face image content, biometric templates, or sensitive personal attributes appeared in the reviewed logs.
- The stack used in-memory processing boundaries already documented for the API; no permanent image storage was added or configured.
- Endpoint responses remained limited to operational health, model metadata, technical capabilities, safety limitations, and metrics.
- The smoke test did not introduce face recognition, identity matching, attractiveness scoring, demographic prediction, health prediction, personality prediction, medical advice, cosmetic advice, or surgery recommendations.

## Next Step

After human review of the production configuration and smoke-test evidence, use `docs/digitalocean-deployment.md` for the first manual Droplet deployment.
