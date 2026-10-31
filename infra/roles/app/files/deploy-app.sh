#!/bin/bash
# Commande forcée de la clé SSH de GitHub Actions (voir le rôle Ansible "app").
# sshd lance CE script quoi que le client demande ; la demande réelle est dans
# SSH_ORIGINAL_COMMAND. Tout ce qui n'est pas explicitement prévu ci-dessous est refusé.
#
# Installé par Ansible, propriétaire root : ne pas le modifier à la main sur le serveur.
set -euo pipefail

# Trace chaque appel dans le journal du système (journalctl -t deploy-app) : on peut
# retrouver qui a demandé quoi, et quand.
journal() { logger -t deploy-app -- "$*"; }

commande="${SSH_ORIGINAL_COMMAND:-}"

case "$commande" in
  # Test de connexion : prouve que la clé, la commande forcée et Docker fonctionnent.
  ping)
    journal "ping"
    echo "pong : utilisateur=$(id -un) hote=$(hostname) architecture=$(uname -m)"
    docker --version
    docker compose version
    ;;

  *)
    # Connexion interactive (commande vide) ou commande inconnue : refus.
    journal "refusé : '${commande}'"
    echo "Commande refusée." >&2
    exit 1
    ;;
esac
