# FaceRatioOps Infrastructure (Terraform)

Infrastructure-as-code for the host that runs FaceRatioOps. It codifies what was
previously a hand-provisioned DigitalOcean Droplet so the host is reproducible and
reviewable. Application rollout stays with the existing image-pull + compose deploy
(`.github/workflows/deploy.yml`); this layer owns the **host**, not the app version.

## What it manages

| Resource | Purpose |
| --- | --- |
| `digitalocean_droplet.api` | The VM. cloud-init installs Docker + compose, enables `ufw`, and creates the deploy dir on first boot. |
| `digitalocean_firewall.api` | Edge firewall: SSH (restricted), 80, 443 in; all out. |
| `cloudflare_record.api` | Proxied `A` record pointing the domain at the Droplet. |

Secrets are never stored in the repo. Tokens come from `TF_VAR_*` environment variables;
SSH keys are referenced by fingerprint (the key must already be uploaded to DigitalOcean).
`terraform.tfvars`, state, and the lock file are gitignored.

## Prerequisites

- Terraform >= 1.6
- A DigitalOcean API token: `export TF_VAR_do_token=...`
- A Cloudflare API token scoped to `Zone:DNS:Edit` for the zone: `export TF_VAR_cloudflare_api_token=...`
- An SSH key uploaded to DigitalOcean (note its fingerprint)
- Your Cloudflare Zone ID

## Usage

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # fill in zone id, ssh fingerprint, your IP

terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

After `apply`, wire the deploy workflow to the new host:

```bash
terraform output droplet_ipv4   # -> set repo secret DROPLET_HOST
terraform output app_url
```

The first deploy still runs through `deploy.yml` (SSH → `git pull` → `docker compose pull`
→ `up -d`) into `deploy_path` (`/opt/faceratioops` by default), which cloud-init created.

## Safety / cost notes

- `prevent_destroy` guards the Droplet; the disk holds app + monitoring volumes. Removing
  the guard and destroying wipes the host.
- A real Droplet and DNS record cost money and are internet-facing. `plan` is free and
  safe to run for review; `apply` provisions live infrastructure.
- Restrict `ssh_allowed_cidrs` to your own IP before `apply`. The default is open.
- Consider remote state (DigitalOcean Spaces / S3 backend) before collaborating — see the
  commented `backend` block in `versions.tf`.
