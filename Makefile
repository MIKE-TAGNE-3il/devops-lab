.PHONY: dev test lint build deploy

# Commandes disponibles au fur et à mesure de l'avancement du projet
# (Phase 2 : dev/build — Phase 3 : test/lint/deploy)

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

test:
	@echo "TODO (Phase 3) : pytest"

lint:
	@echo "TODO (Phase 3) : ruff + eslint"

build:
	docker compose build

deploy:
	@echo "TODO (Phase 3) : déploiement manuel de debug"
