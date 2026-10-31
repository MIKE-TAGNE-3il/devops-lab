# Phase 4 — state distant sur Terraform Cloud (HCP Terraform).
#
# Le state ne va JAMAIS dans Git : il contient les identifiants et attributs réels des
# ressources. Sur Terraform Cloud il est chiffré, versionné, et verrouillé pendant un apply.
#
# Deux workspaces (= deux states indépendants) partagent ce code, repérés par le tag :
#   devops-lab-prod  le VPS de production (importé)
#   devops-lab-test  un serveur jetable pour prouver apply / destroy
# Choisir l'un des deux : `terraform workspace select devops-lab-test`.
#
# Les workspaces doivent être en mode d'exécution « Local » : Terraform tourne sur le PC
# (ou le runner CI) et Terraform Cloud ne fait que stocker le state. Sinon le plan
# s'exécuterait chez HashiCorp, sans notre jeton Hetzner.

terraform {
  cloud {
    organization = "devops-lab-mike"

    workspaces {
      tags = ["devops-lab"]
    }
  }
}
