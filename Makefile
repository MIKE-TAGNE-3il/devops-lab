.PHONY: dev test lint build deploy

# Commandes disponibles au fur et à mesure de l'avancement du projet
# (Phase 2 : dev/build — Phase 3 : test/lint/deploy)

dev:
	@echo "TODO (Phase 2) : docker compose up -d"

test:
	@echo "TODO (Phase 3) : pytest"

lint:
	@echo "TODO (Phase 3) : ruff + eslint"

build:
	@echo "TODO (Phase 2) : docker build backend/frontend"

deploy:
	@echo "TODO (Phase 3) : déploiement manuel de debug"
