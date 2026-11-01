# Production : décrit le VPS EXISTANT des phases 1-3 (importé, pas recréé).
# Chaque valeur doit correspondre à la réalité, sinon `terraform plan` propose une modification.
# Workspace Terraform Cloud : devops-lab-prod
# Renommé depuis "devops-lab-test" (nom d'origine, source de confusion avec le workspace de test).
# Le renommage est une modification SUR PLACE chez Hetzner : pas de redémarrage. Le nom d'hôte
# DANS la VM ne change pas (il est géré par l'OS, donc par Ansible, pas par Terraform).
server_name = "devops-lab-prod"
server_type = "cx23"
location    = "fsn1"
# Hetzner refuse alors toute suppression ou reconstruction, même par un `terraform destroy`
# lancé par erreur dans ce workspace. Pour détruire un jour : repasser à false, appliquer, puis détruire.
protection = true
