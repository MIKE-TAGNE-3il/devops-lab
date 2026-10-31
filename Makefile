.PHONY: dev test lint build deploy

# Commandes à lancer depuis WSL/Linux ("make" n'existe pas sous Windows).
# Prérequis : Python avec le module venv (apt install python3-venv) et, pour le lint
# frontend, Node avec "cd frontend && npm ci" fait une fois.

# Interpréteur utilisé pour créer le venv. La production et la CI sont en Python 3.12 :
# si le "python3" de la machine est une autre version, lancer par exemple
#   make test PYTHON=python3.12
PYTHON ?= python3

# Environnement virtuel du backend, créé au premier lancement (ignoré par git : .venv/).
VENV := backend/.venv

# Fichier "témoin" : make ne reconstruit le venv que si requirements-dev.txt a changé.
$(VENV)/.installed: backend/requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --quiet -r backend/requirements-dev.txt
	touch $@

# Le compose de production exige IMAGE_TAG (voir docker-compose.yml) : en local on l'impose à "dev".
COMPOSE_DEV := IMAGE_TAG=dev docker compose -f docker-compose.yml -f docker-compose.dev.yml

dev:
	$(COMPOSE_DEV) up -d --build

# Tests unitaires du backend (base SQLite en mémoire : ni Docker ni PostgreSQL requis).
test: $(VENV)/.installed
	cd backend && .venv/bin/python -m pytest

# Mêmes vérifications que la CI : ruff (lint + format) sur le backend, ESLint sur le frontend.
lint: $(VENV)/.installed
	cd backend && .venv/bin/python -m ruff check .
	cd backend && .venv/bin/python -m ruff format --check .
	cd frontend && npm run lint

# Construit les images en local (le compose de production seul n'a plus de "build:").
build:
	$(COMPOSE_DEV) build

deploy:
	@echo "TODO (Phase 3) : déploiement manuel de debug"
