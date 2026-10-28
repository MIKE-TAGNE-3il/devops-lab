"""Environnement Alembic : fait le lien entre les migrations, nos modèles et la base."""

from alembic import context

import app.models  # noqa: F401  (enregistre les modèles dans Base.metadata pour l'autogénération)
from app.config import get_settings
from app.db import Base, engine

# Alembic compare cette description (nos modèles) à la base réelle pour proposer une migration.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Mode "offline" : affiche le SQL sans se connecter (alembic upgrade head --sql)."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode normal : se connecte à PostgreSQL avec le même moteur que l'API."""
    with engine.connect() as connection:
        # compare_type : détecte aussi un changement de type de colonne (String(50) -> String(100)).
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
