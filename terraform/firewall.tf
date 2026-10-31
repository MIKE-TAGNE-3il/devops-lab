# Phase 4 — Cloud Firewall Hetzner : filtre le trafic AVANT qu'il atteigne la VM.
# Défense en profondeur : UFW (Ansible) reste actif dans le serveur, ce pare-feu est une
# 2e couche indépendante. Tout ce qui n'est pas listé en entrée est refusé ; la sortie est libre
# (aucune règle sortante : Docker doit pouvoir tirer les images, Let's Encrypt répondre...).
#
# PIÈGE : si le port SSH réel du serveur n'est pas dans var.ssh_ports, on se verrouille dehors.
# Prod : 2222 (SSH durci par Ansible). Serveur neuf : 22 jusqu'au passage d'Ansible.

locals {
  # SSH ouvert à tout Internet : les runners GitHub Actions n'ont pas d'IP fixe. La protection
  # repose sur la clé obligatoire, fail2ban et le port non standard.
  toutes_ips = ["0.0.0.0/0", "::/0"]
}

resource "hcloud_firewall" "main" {
  name = "${var.server_name}-fw"

  rule {
    description = "HTTP (redirection vers HTTPS et challenge Let's Encrypt)"
    direction   = "in"
    protocol    = "tcp"
    port        = "80"
    source_ips  = local.toutes_ips
  }

  rule {
    description = "HTTPS (Traefik)"
    direction   = "in"
    protocol    = "tcp"
    port        = "443"
    source_ips  = local.toutes_ips
  }

  dynamic "rule" {
    for_each = var.ssh_ports
    content {
      description = "SSH (port ${rule.value})"
      direction   = "in"
      protocol    = "tcp"
      port        = tostring(rule.value)
      source_ips  = local.toutes_ips
    }
  }

  rule {
    description = "Ping (diagnostic)"
    direction   = "in"
    protocol    = "icmp"
    source_ips  = local.toutes_ips
  }
}
