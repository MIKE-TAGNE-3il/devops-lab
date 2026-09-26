# Pipeline CI/CD complète avec IaC et déploiement automatisé

Lab DevOps personnel : infra provisionnée avec Terraform, configurée avec Ansible,
application conteneurisée (FastAPI + React + PostgreSQL) servie derrière Traefik,
déployée automatiquement via GitHub Actions.

> Statut : structure initiale du repo. Voir `CLAUDE.md` pour le détail des 4 phases
> et leurs critères de validation.

## Architecture cible

```
Internet → DNS → VPS Hetzner (Ubuntu 24.04)
  └─ Traefik (reverse proxy + TLS Let's Encrypt)
      ├─ Frontend React (Nginx) → app.domaine.com
      ├─ Backend FastAPI → app.domaine.com/api
  └─ PostgreSQL (réseau interne uniquement)
```

## Structure du repo

- `terraform/` — provisioning du VPS (Phase 4)
- `infra/` — configuration serveur avec Ansible (Phase 1)
- `backend/` — API FastAPI (Phase 2)
- `frontend/` — app React/Vite (Phase 2)
- `.github/workflows/` — pipelines CI/CD (Phase 3)
- `docker-compose.yml` — orchestration des conteneurs (Phase 2)

## Prérequis

- Un VPS Hetzner (Ubuntu 24.04) — voir la discussion sur le provisioning
- Terraform >= 1.7, Ansible >= 2.16, Docker + Compose >= 27.x
- Un compte GitHub avec Actions activé

## Démarrage

_À compléter au fur et à mesure des phases._
