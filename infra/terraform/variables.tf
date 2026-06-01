variable "do_token" {
  description = "DigitalOcean API token. Provide via TF_VAR_do_token, never commit it."
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token scoped to DNS edit for the zone. Provide via TF_VAR_cloudflare_api_token."
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for the apex domain (e.g. skyshine.online)."
  type        = string
}

variable "domain" {
  description = "Fully qualified hostname to serve the app from."
  type        = string
  default     = "faceratioops.skyshine.online"
}

variable "region" {
  description = "DigitalOcean region slug."
  type        = string
  default     = "sgp1"
}

variable "droplet_size" {
  description = "Droplet size slug. s-1vcpu-1gb is the practical minimum for the monitoring stack."
  type        = string
  default     = "s-1vcpu-1gb"
}

variable "droplet_image" {
  description = "Droplet base image slug."
  type        = string
  default     = "ubuntu-24-04-x64"
}

variable "ssh_key_fingerprints" {
  description = "Fingerprints of SSH keys already uploaded to DigitalOcean, granted root access to the Droplet."
  type        = list(string)
}

variable "ssh_allowed_cidrs" {
  description = "CIDRs allowed to reach SSH (22). Restrict to your IP; default is open and should be narrowed."
  type        = list(string)
  default     = ["0.0.0.0/0", "::/0"]
}

variable "deploy_path" {
  description = "Directory on the Droplet where the compose project lives (matches deploy.yml)."
  type        = string
  default     = "/opt/faceratioops"
}

variable "tags" {
  description = "Tags applied to the Droplet."
  type        = list(string)
  default     = ["faceratioops", "production"]
}
