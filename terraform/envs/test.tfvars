# Serveur jetable pour prouver `terraform apply` puis `terraform destroy`.
# Workspace Terraform Cloud : devops-lab-test (state séparé de la production)
server_name = "devops-lab-ephemere"
server_type = "cx23"
# cx23 n'est plus disponible à Falkenstein (fsn1) pour de nouvelles créations : on prend Nuremberg.
location = "nbg1"
# Un serveur neuf écoute en SSH sur le port 22 jusqu'au passage d'Ansible (qui le déplace sur 2222).
ssh_ports = [22, 2222]
