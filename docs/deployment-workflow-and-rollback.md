# Production Deploy Workflow And Rollback

FaceRatioOps uses GitHub Actions to deploy the `main` branch to an already prepared DigitalOcean Droplet over SSH. The deployment pulls the prebuilt GHCR image, restarts the Docker Compose stack without building on the Droplet, and verifies operational endpoints.

Production deploys run automatically after the GHCR publish workflow succeeds on `main`. The workflow can still be triggered manually as a release fallback or rollback verification path.

## Workflow File

```text
.github/workflows/deploy.yml
```

The workflow is triggered by:

- `workflow_run` after `Publish Container Image` completes successfully on `main`.
- `workflow_dispatch` for manual release, redeploy, or rollback verification.

It checks out `main`, connects to the Droplet, runs `git pull --ff-only origin main`, pulls `ghcr.io/skyshineth/faceratioops:main`, starts the production Compose stack with `--no-build`, waits for API readiness, and verifies:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/model-info
http://127.0.0.1:8000/metrics
```

It can also run public HTTPS smoke checks against:

```text
https://faceratioops.skyshine.online/health
https://faceratioops.skyshine.online/model-info
https://faceratioops.skyshine.online/metrics
https://faceratioops.skyshine.online/docs
https://faceratioops.skyshine.online/
```

## Required GitHub Secrets

Add these in the repository or `production` environment secrets:

| Secret | Purpose |
| --- | --- |
| `DROPLET_HOST` | Public hostname or IPv4 address for SSH. |
| `DROPLET_USER` | SSH deployment user. |
| `DROPLET_SSH_KEY` | Private key for the deployment user. |
| `DROPLET_SSH_KNOWN_HOSTS` | Verified host key line for strict host key checking. |

Optional secrets:

| Secret | Default | Purpose |
| --- | --- | --- |
| `DROPLET_SSH_PORT` | `22` | SSH port. |
| `DROPLET_DEPLOY_PATH` | `/opt/faceratioops` | Existing repo checkout path on the Droplet. |

Generate `DROPLET_SSH_KNOWN_HOSTS` from a trusted machine and verify the fingerprint against the Droplet console before saving it:

```bash
ssh-keyscan -H faceratioops.skyshine.online
```

Do not commit private keys, host-specific `.env.production`, `.env.monitoring`, API payloads, logs, or screenshots containing sensitive data.

## Droplet Prerequisites

Before running the workflow, complete the manual deployment runbook in `docs/digitalocean-deployment.md` at least once.

The Droplet must already have:

- Docker and Docker Compose plugin installed.
- Git installed.
- The repo cloned at `DROPLET_DEPLOY_PATH`.
- `.env.production` created from `.env.production.example`.
- GHCR image `ghcr.io/skyshineth/faceratioops:main` published by `.github/workflows/publish-image.yml`.
- GHCR package visibility set to public, or Docker logged in on the Droplet with a read-only token.
- Caddy configured for `faceratioops.skyshine.online`.
- Firewall allowing only SSH, HTTP, and HTTPS publicly.
- API bound to `127.0.0.1:8000` through `docker-compose.prod.yml`.

## Automatic Deploy Flow

1. Push or merge changes to `main`.
2. `.github/workflows/publish-image.yml` builds and pushes `ghcr.io/skyshineth/faceratioops:main`.
3. `.github/workflows/deploy.yml` starts after the publish workflow completes successfully.
4. The deploy workflow updates the Droplet, pulls the current GHCR image, restarts the production stack, waits for `/health`, and runs local plus public smoke checks.

If the repository has a protected `production` environment with required reviewers, approve the deployment only after reviewing the change set and risk summary.

## Manual Deploy Fallback

1. Open the repository on GitHub.
2. Go to Actions.
3. Select `Production Deploy`.
4. Select `Run workflow`.
5. Leave public smoke checks enabled after DNS and HTTPS are live.
6. Review the workflow logs for local health, model info, metrics, and public endpoint checks.

## Rollback

Rollback remains manual so production can be pinned to a known-good commit and image tag deliberately.

SSH into the Droplet:

```bash
ssh <user>@<droplet-ip>
cd /opt/faceratioops
```

Find the previous known-good commit:

```bash
git log --oneline -10
```

Check out the previous known-good commit and pull the image configured for that commit:

```bash
git checkout <previous-good-commit>
FACERATIOOPS_IMAGE=ghcr.io/skyshineth/faceratioops:<previous-good-sha> \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml pull api
FACERATIOOPS_IMAGE=ghcr.io/skyshineth/faceratioops:<previous-good-sha> \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-build
```

Verify local endpoints from the Droplet:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/model-info
curl -fsS http://127.0.0.1:8000/metrics
```

Verify public HTTPS endpoints from a local machine:

```bash
curl -fsS https://faceratioops.skyshine.online/health
curl -fsS https://faceratioops.skyshine.online/model-info
curl -fsS https://faceratioops.skyshine.online/metrics
```

After rollback validation, either stay pinned temporarily or return to `main` after a fix:

```bash
git checkout main
git pull --ff-only origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull api
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-build
```

## Post-Deploy Review

After every deployment or rollback, review:

- `docker compose -f docker-compose.yml -f docker-compose.prod.yml ps`
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=100 api`
- Caddy logs for HTTPS routing errors
- `/health`, `/model-info`, `/metrics`, `/docs`, and `/`

Confirm logs do not include raw image bytes, base64 image data, uploaded file contents, biometric templates, identity labels, demographic labels, health labels, personality labels, medical labels, cosmetic labels, or attractiveness labels.
