# 512 MB Budget Droplet Runtime

This runbook is for the temporary lowest-cost deployment path on a 512 MB RAM DigitalOcean Droplet. It is suitable only for a low-traffic portfolio demo. It is not the recommended production size for MediaPipe inference.

The key constraint: do not build the Docker image on the Droplet. Build and publish the image from GitHub Actions, then make the Droplet pull and run the prebuilt image.

## Expected Limits

Use this path only with these constraints:

- One API container.
- One Uvicorn process.
- Caddy on the host.
- No Prometheus or Grafana on the Droplet.
- Small uploads only.
- Low request volume.
- Swap enabled.
- GHCR image pull instead of `docker compose up --build`.

Upgrade to at least 1 GB RAM when you can. Use 2 GB RAM for a cleaner production-style deployment with fewer operational surprises.

## GitHub Image Publish

The workflow `.github/workflows/publish-image.yml` builds the Docker image on GitHub Actions and pushes it to GitHub Container Registry:

```text
ghcr.io/skyshineth/faceratioops:main
ghcr.io/skyshineth/faceratioops:<short-sha>
ghcr.io/skyshineth/faceratioops:<full-sha>
```

After the first successful run, make the GHCR package public if the Droplet should pull anonymously. If the package remains private, log in on the Droplet with a read-only token that has `read:packages`. Do not commit tokens or paste them into docs, logs, screenshots, or shell history.

## Swap Setup

Create a 1 GB swap file:

```bash
sudo fallocate -l 1G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=1024
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

Swap is not a substitute for RAM. It helps avoid immediate out-of-memory failures, but inference may still be slow.

## Production Env

For the 512 MB Droplet, start from the low-memory env example:

```bash
cp .env.production.512mb.example .env.production
```

Review the values:

```text
MAX_UPLOAD_BYTES=2097152
MAX_IMAGE_PIXELS=4000000
MAX_DETECTED_FACES=2
```

Keeping `MAX_DETECTED_FACES=2` allows the API to preserve its multiple-face quality warning behavior. Do not lower it to hide multiple-face detection.

The production Compose file defaults to:

```text
ghcr.io/skyshineth/faceratioops:main
```

If you need to deploy a specific rollback image, set `FACERATIOOPS_IMAGE` in the shell before running Compose. Do not rely on `.env.production` for Compose image interpolation.

## Start The API

Pull and start the prebuilt image:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull api
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-build
```

Verify:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/model-info
curl -fsS http://127.0.0.1:8000/metrics
```

Confirm the API remains loopback-bound:

```text
127.0.0.1:8000->8000/tcp
```

## Disk Hygiene

The 10 GB disk is tight. After a successful deploy and health check, remove old unused images:

```bash
docker image prune -f --filter "until=168h"
```

Do not prune volumes unless you intentionally want to delete monitoring data or other persistent Docker volume state.

## Do Not Run On 512 MB

Avoid these on the 512 MB Droplet:

- `docker compose up --build`
- Prometheus
- Grafana
- Large image uploads
- Load tests
- Multiple Uvicorn workers
- Multiple app containers

## Safety Check

The low-memory path must preserve the same safety boundaries:

- Uploaded images are processed in memory and are not permanently stored.
- Logs do not include raw image bytes, base64 image data, uploaded file contents, biometric templates, identity labels, or sensitive personal attributes.
- Outputs remain technical landmark detection, geometric ratios, confidence values, quality warnings, and operational metadata only.
- Public wording avoids face recognition, identity matching, beauty or attractiveness scoring, demographic prediction, health prediction, personality inference, medical advice, cosmetic advice, and surgery recommendations.
