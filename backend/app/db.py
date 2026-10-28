"""Connexion à PostgreSQL : moteur, session et classe de base des modèles."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

# pool_pre_ping : teste la connexion avant usage. Après un redémarrage de PostgreSQL,
# l'API se reconnecte seule au lieu de renvoyer des erreurs 500.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Classe parente de tous les modèles (tables)."""


def get_db() -> Iterator[Session]:
    """Dépendance FastAPI : une session par requête, toujours fermée à la fin."""
    with SessionLocal() as session:
        yield session
