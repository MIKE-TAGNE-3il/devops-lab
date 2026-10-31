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
| 3. Pipeline CI/CD | GitHub Actions : lint, tests, build, scan Trivy, GHCR, déploiement SSH avec retour arrière | ✅ validée (31/10/2026), voir [Preuves](#preuves-de-la-phase-3) |
| 4. Infrastructure as Code | Terraform : provisioning du VPS, state distant | ⏳ à venir |

Le détail de chaque phase et ses critères de validation sont dans [`CLAUDE.md`](CLAUDE.md).

## Architecture

```
Internet ──► DNS ──► VPS Hetzner (Ubuntu 24.04) ── seuls les ports 80, 443 et SSH sont ouverts
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

## Pipeline CI/CD

```
git push (main)
   │
   ▼  GitHub Actions — ci.yml
 lint backend (ruff) ──┐
 lint frontend (ESLint)┴─► tests (pytest) ─► pour backend ET frontend, en parallèle :
                                              build ─► scan Trivy ─► push GHCR (tag = SHA du commit)
                                                                          │
                                                                          ▼
                              deploy · Environment « production » (limité à la branche main)
                                │  SSH : clé restreinte, empreinte du serveur vérifiée
                                ▼
                    VPS · deploy-app deploy <sha> : pull ─► up --wait ─► test depuis Internet
                                │
                                └─ échec ? retour automatique à la version précédente + alerte Discord
```

- **Sur une pull request** : lint, tests, build et scan tournent, **rien n'est publié ni déployé**.
- **Fail fast** : un lint rouge arrête tout en 30 secondes, avant le moindre build.
- **Déploiement manuel** (ou retour arrière vers une version choisie) : onglet *Actions* →
  *Deploy* → *Run workflow*, avec le SHA d'un commit dont les images sont déjà publiées.

## Preuves de la phase 3

| Critère | Mesure |
|---|---|
| Un push sur `main` déploie en moins de 5 minutes | run de **2 min 25 s**, environ 3 min de bout en bout (job de déploiement : 29 s) |
| Retour arrière en cas d'échec | déploiement volontairement cassé (backend impossible à démarrer, commit `f4a7805`) : le serveur est **revenu seul** à la version précédente, **panne mesurée ≈ 16 s**, job rouge, alerte Discord reçue ; le commit a été annulé par un `revert` |
| Scan de sécurité bloquant | Trivy a détecté 3 failles corrigeables (1 critique) dans l'image du frontend avant toute publication ; corrigées par `apk upgrade` |
| Idempotence du serveur | `ansible-playbook` rejoué : `changed=0` |
| Échec lisible | un lint rouge sur une PR arrête le pipeline, les tests sont ignorés |

## Ce qui est en place

**Serveur (Ansible, idempotent)**
- Utilisateur dédié, SSH par clé uniquement, connexion root et mot de passe désactivés, port non
  standard.
- fail2ban, pare-feu UFW (refus par défaut, seuls SSH, 80 et 443 ouverts).
- Docker CE et Compose, Traefik avec certificats Let's Encrypt, dashboard protégé par mot de
  passe. Les secrets sont dans **Ansible Vault**.
- Rôle `app` : utilisateur `cd` **sans sudo** réservé à la CI, dossier `/opt/devops-lab`,
  `docker-compose.yml` de production, et script de déploiement `deploy-app` (propriété de root).

**Application**
- **Backend** : FastAPI, SQLAlchemy 2, migrations **Alembic**, endpoint `/api/health` (200 si la
  base répond, 503 sinon), CRUD `/api/items` paginé et validé, 10 tests `pytest`.
- **Frontend** : React 18 / Vite, servi par Nginx non-root avec en-têtes de sécurité, repli pour
  application à page unique et proxy `/api`.
- **Images** : Dockerfiles multi-stage, utilisateur non-root, healthchecks, versions épinglées
  (jamais `latest`), dépendances verrouillées (`package-lock.json`). `npm audit --omit=dev` : 0
  vulnérabilité en production ; 6 alertes modérées (`minimatch`) dans la chaîne ESLint, en
  développement uniquement, acceptées en attendant un correctif.

**Pipeline**
- Lint (ruff avec règles de sécurité bandit, ESLint), tests, build Buildx avec cache, scan
  **Trivy** (rapport SARIF dans l'onglet *Security*, échec sur toute faille HIGH/CRITICAL
  corrigeable), publication sur **GHCR**, déploiement SSH, alerte **Discord** sur échec.
- Actions GitHub **épinglées par SHA** de commit, permissions `contents: read` par défaut,
  droits d'écriture limités au seul job qui en a besoin.

## Choix techniques

| Choix | Pourquoi |
|---|---|
| Schémas Pydantic séparés du modèle SQL | le client ne peut imposer ni `id`, ni `created_at`, ni un futur champ sensible (protection contre le *mass assignment*) |
| Service `migrate` à usage unique | l'API ne démarre jamais sur un schéma incomplet, une migration échouée est isolée et lisible, et ça fonctionne avec plusieurs réplicas |
| Réseau `internal: true` pour la base | réduit la surface d'attaque et empêche l'exfiltration depuis la base |
| `nginx-unprivileged` et Node 24 | Nginx sans root ; Node 20 est en fin de vie depuis le 30/04/2026 |
| Proxy Nginx avec résolution DNS à chaque requête | évite l'adresse IP périmée en cache quand le backend est recréé (erreurs 502) |
| Fichier `docker-compose.yml` = production, `docker-compose.dev.yml` ajoute les ports et le `build:` | un oubli sur le serveur ne publie rien |
| `${VARIABLE:?message}` dans le compose, dont `IMAGE_TAG` sans valeur par défaut | refus de démarrer plutôt que de créer une base sans mot de passe, une règle Traefik vide ou de déployer une image au hasard |
| Images taguées par le SHA du commit, jamais `latest` | on sait exactement ce qui tourne, et le retour arrière est un simple redéploiement du tag précédent |
| Scan Trivy **avant** la publication, puis `docker push` de l'image scannée | ce qui est publié est exactement ce qui a été scanné, pas une reconstruction |
| `apk upgrade` dans l'image du frontend | applique les correctifs publiés depuis la construction de l'image de base ; l'utilisateur reste non-root |
| Clé SSH de la CI **restreinte** (`restrict,command="/usr/local/bin/deploy-app"`) | la clé ne peut lancer qu'un script qui déploie une image déjà publiée : pas de shell, pas de `scp` |
| `docker-compose.yml` du serveur **posé par Ansible**, avec contrôle de dérive (sha256) | une clé volée ne peut pas faire exécuter un compose arbitraire (conteneur `privileged`) ; si le compose du dépôt diffère de celui du serveur, le déploiement refuse |
| Utilisateur `cd` distinct, sans sudo | le secret de la CI ne donne pas un accès administrateur au serveur |
| Empreinte du serveur en secret, SSH en mode strict | protège contre l'usurpation du serveur (`StrictHostKeyChecking yes`) |
| Environment GitHub `production` limité à la branche `main` | les secrets de déploiement ne sont lisibles que depuis `main` |
| Action composite pour le déploiement (et non un workflow appelé) | un workflow appelé ne reçoit pas les secrets d'un Environment ; l'action s'exécute dans le job qui déclare l'Environment, et sert à la fois à la CI et au déploiement manuel |
| `up --wait` + test de l'application depuis Internet | « démarré » ne veut pas dire « prêt » : on attend les healthchecks, puis on vérifie DNS, TLS, Traefik, API et base |
| Essais Let's Encrypt en mode « staging » d'abord | évite d'épuiser les limites d'émission du domaine |

## Structure du dépôt

```
infra/          Ansible : rôles common, docker, traefik, app ; inventaire et vault
backend/        API FastAPI : app/, migrations/, tests/, Dockerfile, ruff.toml
frontend/       React/Vite, Dockerfile, nginx.conf, eslint.config.js
docker-compose.yml       production (sans ports, derrière Traefik, images GHCR par IMAGE_TAG)
docker-compose.dev.yml   ajoute le build local et les ports pour le PC
terraform/      provisioning du VPS (Phase 4)
.github/
  workflows/    ci.yml (CI + déploiement), deploy.yml (déploiement manuel), terraform.yml (Phase 4)
  actions/deploy/   action composite de déploiement
```

## Essayer en local

Prérequis : Docker et Docker Compose ≥ 27.

```bash
cp .env.example .env                  # puis remplir POSTGRES_* et mettre DOMAIN=localhost
docker network create traefik-public  # une seule fois (sur le serveur, Ansible le crée)
make dev                              # construit les images en local avec IMAGE_TAG=dev
```

- Application : <http://localhost:8080>
- Documentation interactive de l'API : <http://localhost:8000/api/docs>
- Le compose de production exige `IMAGE_TAG` (aucune valeur par défaut) : `make dev` le fixe à
  `dev`. Pour lancer `docker compose` à la main, ajouter `IMAGE_TAG=dev` à son `.env` local.
- Après une modification du code ou d'un Dockerfile, relancer `make dev` : sans reconstruction,
  Compose réutilise l'image existante.

Qualité (mêmes contrôles que la CI) :

```bash
make lint   # ruff (lint + format) et ESLint
make test   # pytest sur une base SQLite en mémoire
```

`make` s'utilise depuis Linux/WSL : il crée un environnement virtuel dans `backend/.venv`
(`make test PYTHON=python3.12` si le `python3` du poste n'est pas en 3.12, comme la CI) ; le lint
frontend demande Node et un `npm ci` préalable dans `frontend/`.

## Déployer

### Première installation

1. **Configurer le serveur** (depuis `infra/`, en WSL : `export ANSIBLE_CONFIG=$PWD/ansible.cfg`,
   car un dossier monté depuis Windows est refusé par Ansible comme source de configuration) :
   ```bash
   ansible-playbook playbooks/setup.yml --ask-vault-pass
   ```
   Les variables `domain` et `acme_staging` (`group_vars/all/all.yml`) choisissent le nom de
   domaine et le serveur Let's Encrypt. Les secrets (`vault_acme_email`,
   `vault_traefik_dashboard_password`) sont dans le vault chiffré. La clé publique de la CI est
   `ci_deploy_public_key` ; la clé privée correspondante ne vit que dans GitHub.
2. **Créer le `.env` de l'application** sur le serveur : `/opt/devops-lab/.env`, propriétaire
   `cd`, mode `0600`, avec `POSTGRES_*` et `DOMAIN` (sans `IMAGE_TAG` : c'est le déploiement qui
   le fournit).
3. **Configurer GitHub** :
   - Environment `production`, limité à la branche `main`, avec les **secrets** `SSH_PRIVATE_KEY`
     et `SSH_KNOWN_HOSTS` (ligne `[ip]:port ssh-ed25519 …`) et les **variables** `SSH_HOST`,
     `SSH_PORT`, `SSH_USER` (`cd`) et `APP_DOMAIN` (`app.<domaine>`) ;
   - secret **de dépôt** `DISCORD_WEBHOOK` (alertes).

### Déploiements courants

Un push sur `main` suffit : la CI construit, scanne, publie, déploie et vérifie. Un déploiement
raté revient seul à la version précédente.

Si le `docker-compose.yml` change, **relancer Ansible avant** (il est posé par Ansible) : sinon
le déploiement refuse avec « docker-compose.yml du serveur différent de celui du commit ».

### Déploiement ou retour arrière manuel

Onglet *Actions* → *Deploy* → *Run workflow*, avec le SHA complet d'un commit dont les images sont
publiées. Le script du serveur offre aussi `status` et `rollback` (version précédente) à qui
détient la clé de la CI :

```bash
ssh -i ~/.ssh/devops_lab_ci -p 2222 cd@<ip> status
ssh -i ~/.ssh/devops_lab_ci -p 2222 cd@<ip> rollback
```

## Limites connues

Ce lab est un projet d'apprentissage ; voici ce qu'il ne fait pas encore :

- **Pas d'authentification** sur l'API : le CRUD est ouvert. Acceptable pour une démonstration,
  pas pour de vraies données.
- **Le retour arrière ne défait pas les migrations** de base de données : elles doivent rester
  compatibles avec la version précédente du code (ajouter d'abord, supprimer plus tard).
- **Pas de déploiement sans coupure** : les conteneurs sont recréés (`up --wait`), ce qui coupe
  l'application quelques secondes (≈ 16 s mesurées lors d'un retour arrière). Un blue/green
  derrière Traefik serait la suite logique.
- **Le premier déploiement n'a pas de version précédente** vers laquelle revenir.
- **Le compose de production est posé par Ansible** : une modification demande de relancer
  Ansible avant le déploiement (contrôle de dérive, voulu).
- **Les images GHCR sont publiques** (le dépôt l'est aussi, elles ne contiennent aucun secret) ;
  rien à configurer sur le serveur pour les tirer.
- **La documentation interactive de l'API** (`/api/docs`) est publique.
- **Nom de domaine gratuit** (sslip.io) dont les limites Let's Encrypt sont partagées ; un domaine
  dédié ne demanderait de changer qu'une variable.
- Le **provisioning Terraform** (phase 4) n'est pas encore écrit : le serveur n'est pas encore
  géré comme du code.
