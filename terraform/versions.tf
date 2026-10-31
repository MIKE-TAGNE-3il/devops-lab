# Phase 4 — versions de Terraform et du provider Hetzner Cloud.
#
# Le jeton d'API n'est PAS ici : le provider lit la variable d'environnement HCLOUD_TOKEN
# (PC : `$env:HCLOUD_TOKEN = ...` ; CI : secret GitHub). Ainsi, aucun secret dans le code.

terraform {
  required_version = ">= 1.7"

  required_providers {
    hcloud = {
      source = "hetznercloud/hcloud"
      # "~> 1.70" accepte 1.70 et plus récent mais reste en 1.x : les changements
      # incompatibles n'arrivent qu'en 2.0. Le fichier .terraform.lock.hcl (versionné)
      # fige en plus la version exacte et son empreinte.
      version = "~> 1.70"
    }
  }
}

provider "hcloud" {}
