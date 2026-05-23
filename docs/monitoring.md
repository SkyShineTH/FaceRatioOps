# Prometheus And Grafana Monitoring Runbook

This runbook adds optional production monitoring for FaceRatioOps after the API is stable behind HTTPS. It uses Prometheus to scrape the API's `/metrics` endpoint and Grafana to display request rate, latency, status/error rate, and service scrape health.

Monitoring must remain operational-only. Do not add image payloads, uploaded file names, biometric templates, identity labels, demographic attributes, health attributes, appearance judgments, or personal attributes to metrics or dashboard labels.

## Included Files

| File | Purpose |
| --- | --- |
| `docker-compose.monitoring.yml` | Optional Compose override for Prometheus and Grafana. |
| `.env.monitoring.example` | Non-secret Grafana defaults to copy into `.env.monitoring`. |
| `deploy/prometheus/prometheus.yml` | Prometheus scrape config for `api:8000/metrics`. |
| `deploy/grafana/provisioning/datasources/prometheus.yml` | Grafana Prometheus datasource provisioning. |
| `deploy/grafana/provisioning/dashboards/faceratioops.yml` | Grafana dashboard provider. |
| `deploy/grafana/dashboards/faceratioops-overview.json` | Operations dashboard JSON. |

The API metrics exposed by FaceRatioOps use only `method`, `path`, and `status` labels. Prometheus will also attach its standard scrape labels such as `job` and `instance`; do not add custom labels containing user, image, or biometric data.

## Start Monitoring

Create a local monitoring env file on the host:

```bash
cp .env.monitoring.example .env.monitoring
```

Edit `.env.monitoring` and replace `GF_SECURITY_ADMIN_PASSWORD` with a long random password. Do not commit `.env.monitoring`.

Start the API and monitoring services:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  --profile monitoring \
  up -d --build
```

Verify service status:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  --profile monitoring \
  ps
```

Prometheus and Grafana bind to loopback only:

```text
127.0.0.1:9090 -> Prometheus
127.0.0.1:3000 -> Grafana
```

For a remote Droplet, access them through an SSH tunnel:

```bash
ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 <user>@<droplet-ip>
```

Then open:

```text
http://127.0.0.1:3000
http://127.0.0.1:9090
```

## Verify Prometheus

Check Prometheus health:

```bash
curl -fsS http://127.0.0.1:9090/-/healthy
```

Check the API target:

```bash
curl -fsS http://127.0.0.1:9090/api/v1/targets
```

Generate safe operational traffic:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/model-info
curl -fsS http://127.0.0.1:8000/metrics
```

Query request metrics:

```bash
curl -fsS "http://127.0.0.1:9090/api/v1/query?query=faceratioops_http_requests_total"
```

The response must show route/status/method operational series only. It must not include uploaded image contents, face image data, identity data, demographic attributes, health attributes, attractiveness labels, medical labels, or cosmetic labels.

## Grafana Dashboard

The provisioned dashboard is named `FaceRatioOps Operations Overview`.

Panels:

- Request rate
- 5xx error ratio
- Prometheus scrape health
- Request rate by route and status
- Average request duration by route
- Status rate

Capture screenshots only after confirming no secrets, private IP addresses that should not be public, uploaded images, logs, or personal data are visible.

## Stop Monitoring

Stop only the monitoring services:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  --profile monitoring \
  stop prometheus grafana
```

Stop the full stack:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  --profile monitoring \
  down
```

Remove monitoring data volumes only when you intentionally want to discard local metrics and dashboard state:

```bash
docker volume rm faceratioops_prometheus-data faceratioops_grafana-data
```

## Safety Check

Before publishing monitoring evidence, confirm:

- API image uploads are still processed in memory only.
- No uploaded image payloads, base64 image data, biometric templates, identity labels, or sensitive personal attributes appear in logs or metrics.
- Dashboard screenshots show operational service behavior only.
- Metrics labels remain limited to operational HTTP dimensions.
- Public wording describes technical landmark detection and geometric ratio analysis only.
