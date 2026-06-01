output "droplet_ipv4" {
  description = "Public IPv4 of the Droplet. Use as DROPLET_HOST in the deploy workflow."
  value       = digitalocean_droplet.api.ipv4_address
}

output "droplet_urn" {
  description = "DigitalOcean URN of the Droplet."
  value       = digitalocean_droplet.api.urn
}

output "app_url" {
  description = "Public URL once DNS has propagated and Caddy has issued a certificate."
  value       = "https://${var.domain}"
}

output "deploy_path" {
  description = "Compose project directory created on the Droplet by cloud-init."
  value       = var.deploy_path
}
