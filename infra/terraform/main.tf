# FaceRatioOps infrastructure: a single DigitalOcean Droplet running the Docker Compose
# stack, fronted by Caddy (HTTPS) and a Cloudflare-proxied DNS record.
#
# This codifies the host that deploy.yml ships to. It provisions the Droplet, locks
# down the network, and points DNS at it; application rollout stays with the existing
# image-pull + compose deploy workflow. No secrets live in this repo — tokens come from
# TF_VAR_* environment variables and SSH keys are referenced by fingerprint.

locals {
  hostname = replace(var.domain, ".", "-")
}

# cloud-init installs Docker Engine + the compose plugin and prepares the deploy dir,
# so the Droplet is ready for the SSH deploy workflow on first boot.
data "cloudinit_config" "bootstrap" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content = yamlencode({
      package_update  = true
      package_upgrade = true
      packages        = ["ca-certificates", "curl", "git", "ufw"]
      runcmd = [
        "install -m 0755 -d /etc/apt/keyrings",
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
        "chmod a+r /etc/apt/keyrings/docker.asc",
        "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable\" > /etc/apt/sources.list.d/docker.list",
        "apt-get update",
        "apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
        "systemctl enable --now docker",
        "ufw default deny incoming",
        "ufw default allow outgoing",
        "ufw allow 22/tcp",
        "ufw allow 80/tcp",
        "ufw allow 443/tcp",
        "ufw --force enable",
        "mkdir -p ${var.deploy_path}",
      ]
    })
  }
}

resource "digitalocean_droplet" "api" {
  name       = local.hostname
  image      = var.droplet_image
  region     = var.region
  size       = var.droplet_size
  ssh_keys   = var.ssh_key_fingerprints
  user_data  = data.cloudinit_config.bootstrap.rendered
  monitoring = true
  tags       = var.tags

  lifecycle {
    # The disk holds the deployed app, compose files, and monitoring volumes. Guard
    # against an accidental replacement that would wipe the host.
    prevent_destroy = true
  }
}

# Network firewall at the DigitalOcean edge, in addition to the host ufw rules.
resource "digitalocean_firewall" "api" {
  name        = "${local.hostname}-fw"
  droplet_ids = [digitalocean_droplet.api.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_cidrs
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Cloudflare-proxied DNS record. Proxied = true keeps the origin IP hidden and routes
# through Cloudflare; Caddy on the Droplet terminates TLS for the origin.
resource "cloudflare_record" "api" {
  zone_id = var.cloudflare_zone_id
  name    = var.domain
  content = digitalocean_droplet.api.ipv4_address
  type    = "A"
  proxied = true
  ttl     = 1 # 1 = automatic; required when proxied.
  comment = "FaceRatioOps API origin (managed by Terraform)."
}
