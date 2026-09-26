# CLAUDE.md — Projet DevOps Lab

## Contexte du projet

Ce projet est un lab DevOps personnel déployé sur un serveur dédié Hetzner. Il sert de preuve de compétences pour un CV de stage DevOps/DevSecOps. Chaque composant doit être fonctionnel, déployé, et défendable en entretien technique.

**Propriétaire :** Mike — étudiant ingénieur cybersécurité (BAC+5), 3iL Ingénieurs, Limoges.
**Objectif :** Construire une pipeline CI/CD complète avec IaC, conteneurisation, et déploiement automatisé sur un serveur réel.

## Architecture cible

```
Internet → DNS (domaine) → VPS Hetzner (Ubuntu 24.04)
  └─ Traefik (reverse proxy + TLS Let's Encrypt)
      ├─ Frontend React (Nginx) → app.domaine.com
      ├─ Backend FastAPI → app.domaine.com/api
      └─ (futur) Grafana, ArgoCD, etc.
  └─ PostgreSQL (réseau interne uniquement)
```

**Infra provisionnée par :** Terraform (Hetzner provider)
**Serveur configuré par :** Ansible (playbooks idempotents)
**App conteneurisée avec :** Docker + Docker Compose
**CI/CD :** GitHub Actions → GHCR → déploiement SSH sur le VPS
**Sécurité :** SSH par clé, fail2ban, UFW, scan Trivy, secrets dans GitHub Secrets

## Structure du repo

```
devops-lab/
├── CLAUDE.md                  # Ce fichier
├── README.md                  # Documentation publique du projet
├── terraform/                 # Provisioning du VPS Hetzner
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf
├── infra/                     # Configuration serveur Ansible
│   ├── inventory/
│   │   └── hosts.yml
│   ├── playbooks/
│   │   └── setup.yml
│   ├── roles/
│   │   ├── common/            # Users, SSH, fail2ban, UFW
│   │   ├── docker/            # Docker CE + Compose
│   │   └── traefik/           # Reverse proxy + TLS
│   └── group_vars/
│       └── all.yml
├── backend/                   # API FastAPI
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # App React (Vite)
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml         # Orchestration locale et production
├── .env.example               # Variables d'environnement (template)
├── Makefile                   # Commandes utilitaires
└── .github/
    └── workflows/
        ├── ci.yml             # Lint, test, build, scan, push GHCR
        ├── deploy.yml         # Déploiement sur le VPS
        └── terraform.yml      # Plan/Apply Terraform
```

## Phases du projet

Le projet se réalise en 4 semaines séquentielles. Ne jamais sauter une phase.

### Phase 1 — Fondations serveur (Ansible)
- **Statut :** EN COURS (structure du repo posée)
- Playbook Ansible pour configurer le VPS from scratch
- Roles : common (SSH hardening, fail2ban, UFW), docker, traefik
- Tout est idempotent et utilise les modules Ansible natifs
- **Critère de validation :** `ansible-playbook setup.yml` configure un serveur vierge en < 5 min

### Phase 2 — Conteneurisation (Docker)
- **Statut :** À FAIRE
- App FastAPI + React + PostgreSQL conteneurisée
- Dockerfiles multi-stage (images légères, user non-root)
- docker-compose.yml avec healthchecks, réseaux séparés, labels Traefik
- **Critère de validation :** `docker compose up -d` lance tout, l'app est accessible en HTTPS

### Phase 3 — Pipeline CI/CD (GitHub Actions)
- **Statut :** À FAIRE
- CI : lint (ruff + eslint), tests (pytest), build images, scan Trivy, push GHCR
- CD : déploiement SSH, rolling update, rollback en cas d'échec
- Notifications Discord sur échec
- **Critère de validation :** un push sur main déclenche le déploiement automatique en < 5 min

### Phase 4 — Terraform (IaC)
- **Statut :** À FAIRE
- Provisioning du VPS Hetzner via Terraform
- State en remote (Terraform Cloud)
- `terraform plan` intégré à la CI sur les PR
- **Critère de validation :** `terraform apply` crée un VPS fonctionnel, `terraform destroy` le supprime

## Conventions de code

### Général
- Langue du code et des commentaires : **français**
- Langue de la documentation (README, docs/) : **français** (c'est pour un CV français)
- Pas de secrets en dur, jamais. Tout passe par des variables d'environnement ou Ansible Vault
- Tout fichier créé doit être versionné dans Git sauf : .env, .terraform/, *.tfstate*, node_modules/, __pycache__/

### Ansible
- Utiliser les modules natifs Ansible (apt, copy, template, service, ufw...) — PAS de module shell/command sauf si aucun module natif n'existe
- Chaque tâche a un `name:` descriptif en anglais
- Handlers pour redémarrer les services quand leur config change
- Variables dans group_vars, jamais en dur dans les tasks

### Docker
- Images de base : versions spécifiques (python:3.12-slim, node:20-alpine, nginx:alpine) — JAMAIS `latest`
- Multi-stage builds obligatoires
- User non-root dans les images de production
- Healthchecks dans chaque Dockerfile et dans docker-compose.yml
- Un .dockerignore dans chaque dossier avec un Dockerfile

### GitHub Actions
- Les secrets viennent exclusivement de GitHub Secrets
- Fail fast : lint → tests → build → scan → deploy
- Images taggées avec le SHA du commit, pas `latest` en production
- Chaque workflow a un commentaire en en-tête expliquant ce qu'il fait

### Terraform
- terraform fmt appliqué systématiquement
- Pas de valeurs par défaut pour les secrets (variables marked sensitive)
- State JAMAIS dans le repo Git

## Règles pour Claude Code

1. **Explique avant de coder.** Avant chaque bloc de code significatif, explique en 2-3 phrases ce que ça fait et pourquoi. Mike doit pouvoir défendre chaque ligne en entretien.

2. **Ne saute pas les étapes.** Respecte l'ordre des phases. Si Mike demande la phase 3 alors que la phase 1 n'est pas validée, signale-le.

3. **Propose, ne décide pas seul.** Pour les choix d'architecture (quelle image de base, quel port, quelle structure), propose 2 options avec les trade-offs et laisse Mike choisir.

4. **Teste chaque étape.** Après chaque composant créé, donne la commande pour vérifier que ça marche. Ne passe pas au suivant sans validation.

5. **Signale les pièges.** Si quelque chose risque de casser en production ou de poser un problème de sécurité, dis-le immédiatement, même si Mike n'a pas demandé.

6. **Code propre et commenté.** Chaque fichier de configuration a des commentaires expliquant les choix non évidents. Pas de code copié-collé sans compréhension.

7. **Mets à jour ce fichier.** Quand une phase est terminée, mets à jour le statut dans la section "Phases du projet" de ce CLAUDE.md.

## Informations serveur (à remplir après location)

```
VPS_IP=
DOMAIN=
SSH_PORT=
SSH_USER=deploy
```

## Stack technique complète

| Composant | Outil | Version |
|---|---|---|
| OS serveur | Ubuntu | 24.04 LTS |
| Hyperviseur local | WSL2 | Ubuntu 24.04 |
| IaC - Provisioning | Terraform | >= 1.7 |
| IaC - Configuration | Ansible | >= 2.16 |
| Conteneurisation | Docker + Compose | >= 27.x |
| Reverse proxy | Traefik | 3.x |
| Backend | FastAPI (Python) | 3.12 |
| Frontend | React (Vite) | 18.x |
| Base de données | PostgreSQL | 16 |
| CI/CD | GitHub Actions | - |
| Registry | GHCR | - |
| Scan sécurité | Trivy | latest |
| Lint Python | Ruff | latest |
| Lint JS | ESLint | latest |
| Tests Python | Pytest | latest |
