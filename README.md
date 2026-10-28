# DevOps Lab — pipeline CI/CD avec IaC et déploiement automatisé

Lab DevOps personnel, déployé sur un serveur dédié Hetzner : infrastructure provisionnée avec
Terraform, serveur configuré avec Ansible, application conteneurisée (FastAPI + React +
PostgreSQL) servie en HTTPS derrière Traefik, déployée automatiquement via GitHub Actions.

L'objectif est un projet **fonctionnel, déployé et défendable** : chaque choix technique est
justifié (voir [Choix techniques](#choix-techniques)).

## Avancement

| Phase | Contenu | Statut |
|---|---|---|
| 1. Fondations serveur | Ansible : durcissement SSH, fail2ban, UFW, Docker, Traefik | ✅ validée, idempotence prouvée (`changed=0`) |
| 2. Conteneurisation | Docker : API, frontend, base, réseaux isolés, HTTPS | ✅ validée |
| 3. Pipeline CI/CD | GitHub Actions : lint, tests, build, scan Trivy, GHCR, déploiement SSH | ⏳ à venir |
| 4. Infrastructure as Code | Terraform : provisioning du VPS, state distant | ⏳ à venir |

Le détail de chaque phase et ses critères de validation sont dans [`CLAUDE.md`](CLAUDE.md).

## Architecture

```
Internet ──► DNS ──► VPS Hetzner (Ubuntu 24.04) ── seuls les ports 80 et 443 sont ouverts
                       │
                       └─ Traefik (reverse proxy, HTTPS Let's Encrypt, redirection HTTP→HTTPS)
                            │            réseau « traefik-public »
                            ├─ app.<domaine>        ──► frontend  (React compilé, Nginx non-root)
                            └─ app.<domaine>/api    ──► backend   (FastAPI)
                                                          │        réseau « internal »
                                                          └──────► PostgreSQL 16
```

- **Deux zones réseau.** Le frontend et le backend sont sur `traefik-public`. La base est
  **seule** sur `internal`, un réseau sans accès à Internet : même si le frontend était compromis,
  il ne pourrait pas la joindre, et la base ne pourrait pas exfiltrer de données. Le backend est
  le seul pont entre les deux zones.
- **Aucun port publié** par les conteneurs : Traefik atteint le frontend et le backend par le
  réseau interne de Docker.
- **Ordre de démarrage garanti** : base saine → migrations terminées avec succès → backend sain
  → frontend.

## Ce qui est en place

**Serveur (Ansible, idempotent)**
- Utilisateur dédié, SSH par clé uniquement, connexion root et mot de passe désactivés, port non
  standard.
- fail2ban, pare-feu UFW (refus par défaut, seuls SSH, 80 et 443 ouverts).
- Docker CE et Compose, Traefik avec certificats Let's Encrypt, dashboard protégé par mot de
  passe. Les secrets sont dans **Ansible Vault**.

**Application**
- **Backend** : FastAPI, SQLAlchemy 2, migrations **Alembic**, endpoint `/api/health` (200 si la
  base répond, 503 sinon), CRUD `/api/items` paginé et validé, 10 tests `pytest`.
- **Frontend** : React 18 / Vite, servi par Nginx non-root avec en-têtes de sécurité, repli pour
  application à page unique et proxy `/api`.
- **Images** : Dockerfiles multi-stage, utilisateur non-root, healthchecks, versions épinglées
  (jamais `latest`), dépendances verrouillées (`package-lock.json`, `npm audit` : 0 vulnérabilité).

## Choix techniques

| Choix | Pourquoi |
|---|---|
| Schémas Pydantic séparés du modèle SQL | le client ne peut imposer ni `id`, ni `created_at`, ni un futur champ sensible (protection contre le *mass assignment*) |
| Service `migrate` à usage unique | l'API ne démarre jamais sur un schéma incomplet, une migration échouée est isolée et lisible, et ça fonctionne avec plusieurs réplicas |
| Réseau `internal: true` pour la base | réduit la surface d'attaque et empêche l'exfiltration depuis la base |
| `nginx-unprivileged` et Node 24 | Nginx sans root ; Node 20 est en fin de vie depuis le 30/04/2026 |
| Proxy Nginx avec résolution DNS à chaque requête | évite l'adresse IP périmée en cache quand le backend est recréé (erreurs 502) |
| Fichier `docker-compose.yml` = production, `docker-compose.dev.yml` ajoute les ports | un oubli sur le serveur ne publie rien |
| `${VARIABLE:?message}` dans le compose | refus de démarrer plutôt que de créer une base sans mot de passe ou une règle Traefik vide |
| Essais Let's Encrypt en mode « staging » d'abord | évite d'épuiser les limites d'émission du domaine |

## Structure du dépôt

```
infra/          Ansible : rôles common, docker, traefik ; inventaire et vault
backend/        API FastAPI : app/, migrations/, tests/, Dockerfile
frontend/       React/Vite, Dockerfile, nginx.conf
docker-compose.yml       production (sans ports, derrière Traefik)
docker-compose.dev.yml   ajoute les ports pour le PC
terraform/      provisioning du VPS (Phase 4)
.github/        pipelines CI/CD (Phase 3)
```

## Essayer en local

Prérequis : Docker et Docker Compose ≥ 27.

```bash
cp .env.example .env                  # puis remplir POSTGRES_* et mettre DOMAIN=localhost
docker network create traefik-public  # une seule fois (sur le serveur, Ansible le crée)
make dev                              # ou : docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

- Application : <http://localhost:8080>
- Documentation interactive de l'API : <http://localhost:8000/api/docs>
- Après une modification du code ou d'un Dockerfile, relancer avec `--build` : sans cela,
  Compose réutilise l'image existante.

Tests et lint du backend :

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest
python -m ruff check .
```

## Déployer sur un serveur

1. Configurer le serveur (depuis `infra/`) :
   ```bash
   ansible-playbook -i inventory/hosts.yml playbooks/setup.yml --ask-vault-pass
   ```
   Les variables `domain` (`group_vars/all/all.yml`) et `acme_staging` choisissent le nom de
   domaine et le serveur Let's Encrypt (test ou production). Les secrets
   (`vault_acme_email`, `vault_traefik_dashboard_password`) sont dans le vault chiffré.
2. Sur le serveur : cloner le dépôt, créer le `.env` (`DOMAIN` = le domaine, nouveaux mots de
   passe), puis `docker compose up -d --build`.

## Limites connues

Ce lab est un projet d'apprentissage ; voici ce qu'il ne fait pas encore :

- **Pas d'authentification** sur l'API : le CRUD est ouvert. Acceptable pour une démonstration,
  pas pour de vraies données.
- **Images construites sur le serveur** : le déploiement par images versionnées (GHCR, tag = SHA du
  commit) et le retour arrière arrivent avec la phase 3.
- **La documentation interactive de l'API** (`/api/docs`) est publique.
- **Nom de domaine gratuit** (sslip.io) dont les limites Let's Encrypt sont partagées ; un domaine
  dédié ne demanderait de changer qu'une variable.
- Le **provisioning Terraform** (phase 4) n'est pas encore écrit : le serveur n'est pas encore
  géré comme du code.
