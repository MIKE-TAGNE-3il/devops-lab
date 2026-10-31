# Production : décrit le VPS EXISTANT des phases 1-3 (importé, pas recréé).
# Chaque valeur doit correspondre à la réalité, sinon `terraform plan` propose une modification.
# Workspace Terraform Cloud : devops-lab-prod
server_name = "devops-lab-test" # nom historique du serveur ; renommage prévu plus tard, via le code
server_type = "cx23"
location    = "fsn1"
# Hetzner refuse alors toute suppression ou reconstruction, même par un `terraform destroy`
# lancé par erreur dans ce workspace. Pour détruire un jour : repasser à false, appliquer, puis détruire.
protection = true
