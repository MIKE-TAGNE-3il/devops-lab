# Phase 4 — valeurs utiles après un apply (inventaire Ansible, tests).

output "server_id" {
  description = "Identifiant Hetzner du serveur"
  value       = hcloud_server.main.id
}

output "ipv4_address" {
  description = "Adresse IPv4 publique (à mettre dans infra/inventory/hosts.yml)"
  value       = hcloud_server.main.ipv4_address
}

output "ipv6_address" {
  description = "Adresse IPv6 publique"
  value       = hcloud_server.main.ipv6_address
}
