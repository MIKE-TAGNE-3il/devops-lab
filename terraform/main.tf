# Phase 4 — le serveur Hetzner Cloud. Il est ensuite configuré par Ansible (dossier infra/).

# Clé SSH déjà présente dans le projet : on la LIT (data) au lieu de la créer, car Hetzner
# refuse deux clés avec la même clé publique (le workspace de test échouerait).
data "hcloud_ssh_key" "admin" {
  name = var.ssh_key_name
}

resource "hcloud_server" "main" {
  name        = var.server_name
  server_type = var.server_type
  location    = var.location
  image       = var.image
  ssh_keys    = [data.hcloud_ssh_key.admin.id]

  # Pare-feu Hetzner (firewall.tf) : attaché au serveur, y compris à la création.
  firewall_ids = [hcloud_firewall.main.id]

  # Les deux protections vont ensemble : Hetzner exige la même valeur pour les deux.
  delete_protection  = var.protection
  rebuild_protection = var.protection

  # IPv4 et IPv6 publiques sont activées par défaut : pas de bloc public_net. L'import ne
  # remplit pas ce bloc dans le state, donc l'écrire ferait apparaître un écart artificiel.

  lifecycle {
    # L'API ne renvoie jamais ces champs pour un serveur existant (ils ne servent qu'à la
    # création). Sans cette ligne, un serveur IMPORTÉ semblerait avoir changé et Terraform
    # voudrait le recréer.
    ignore_changes = [ssh_keys, user_data]
  }
}
