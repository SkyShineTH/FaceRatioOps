# GitHub Security And Quality Setup

This checklist captures the repository security and quality setup for FaceRatioOps. Some controls are represented as committed files; others must be enabled in GitHub repository settings.

## Committed Controls

| Control | File |
| --- | --- |
| CI lint, tests, and Docker build | `.github/workflows/ci.yml` |
| Image vulnerability scan (Trivy) + SBOM (Syft) | `.github/workflows/ci.yml` (backend job) |
| Monitoring rule + Terraform validation | `.github/workflows/ci.yml` (config-validate job) |
| GHCR image publish | `.github/workflows/publish-image.yml` |
| Manual production deployment | `.github/workflows/deploy.yml` |
| CodeQL advanced setup for Python | `.github/workflows/codeql.yml` |
| Dependabot version updates | `.github/dependabot.yml` |

CI builds the production image, generates an SPDX SBOM (uploaded as an artifact), and
scans it with Trivy. Trivy results are uploaded as SARIF to GitHub code scanning, and the
build fails on fixable CRITICAL/HIGH vulnerabilities (`ignore-unfixed: true` so base-image
issues without an available fix do not block merges). The `config-validate` job runs
`promtool check rules` on the Prometheus alerting/recording rules and `terraform validate`
on the infrastructure code.

CI has read-only `GITHUB_TOKEN` permissions by default; the backend job additionally
requests `security-events: write` only to upload the Trivy SARIF report. The manual deploy workflow is `workflow_dispatch` only and uses SSH secrets scoped to GitHub Actions.

## GitHub Settings To Enable

Enable these after the public deployment is stable:

- Dependabot alerts
- Dependabot security updates
- Secret scanning
- Push protection, if available for the repository plan
- Code scanning alerts for the CodeQL workflow
- Branch protection or a ruleset for `main`

Recommended `main` branch protection:

- Require pull request before merge.
- Require status checks before merge.
- Require `CI / Lint, test, and build`.
- Require CodeQL analysis once the workflow has produced a stable check name.
- Block force pushes.
- Block branch deletion.
- Require conversation resolution.
- Require deployment workflow changes to receive human review before merge.

## Deploy Key Guidance

The first production deployment can clone a public repository over HTTPS and does not require a deploy key.

Use a read-only GitHub Deploy key only if the repository becomes private or the Droplet must pull over SSH:

```bash
ssh-keygen -t ed25519 -C "faceratioops-droplet-readonly"
```

Add the public key in GitHub as a read-only Deploy key. Keep the private key only on the Droplet. Do not commit keys or add private keys to docs, screenshots, logs, issue comments, or workflow output.

## Human Review Gates

Require human review before merging changes that affect:

- Inference behavior or landmark/ratio calculation logic.
- API response schemas.
- Image upload, processing, retention, or logging behavior.
- Safety-sensitive wording in README, docs, UI, or API messages.
- Docker, Caddy, GitHub Actions, monitoring, deployment, or production configuration.
- Public portfolio language.

## Safety Review

Before publishing GitHub security or workflow evidence, confirm:

- No secrets are present in repository files, logs, screenshots, or Actions output.
- `.env.production` and `.env.monitoring` remain untracked.
- Workflow logs do not print SSH keys, environment file contents, image payloads, or sensitive request data.
- Public copy avoids identity matching, attractiveness scoring, demographic prediction, health prediction, personality inference, medical advice, cosmetic advice, and surgery recommendations.
