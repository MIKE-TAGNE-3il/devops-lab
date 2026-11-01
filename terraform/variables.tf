# Phase 4 — variables. Les valeurs propres à chaque environnement sont dans envs/*.tfvars
# (aucun secret : le jeton d'API passe par HCLOUD_TOKEN, jamais par une variable).
# Usage : terraform plan -var-file=envs/prod.tfvars

variable "server_name" {
  description = "Nom du serveur dans Hetzner Cloud"
  type        = string
}

variable "server_type" {
  description = "Type de serveur (ex. cx23). Le changer redimensionne ou recrée le serveur"
  type        = string
}

variable "location" {
  description = "Région Hetzner (fsn1, nbg1, hel1...). La changer RECRÉE le serveur : le type doit y être disponible"
  type        = string
}

variable "image" {
  description = "Image système du serveur"
  type        = string
  default     = "ubuntu-24.04"
}

variable "ssh_key_name" {
  description = "Nom de la clé SSH DÉJÀ présente dans le projet Hetzner (lue, pas créée : Hetzner refuse deux clés identiques)"
  type        = string
  default     = "mike-devops-lab"
}

variable "ssh_ports" {
  description = "Ports SSH ouverts dans le pare-feu. Un port absent de la liste = on se verrouille dehors"
  type        = list(number)
  default     = [2222]
}

variable "protection" {
  description = "Protège le serveur contre la suppression et la reconstruction (true en production)"
  type        = bool
  default     = false
}
