"""Configuration commune des tests."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Doit être défini AVANT l'import de l'app : app.db crée le moteur à l'import.
# SQLite en mémoire : les tests unitaires n'ont pas besoin de PostgreSQL.
os.environ.setdefault("DATABASE_URL", "sqlite://")


@pytest.fixture
def client():
    """Client de test branché sur une base SQLite vierge, recréée pour chaque test."""
    # Imports ici et non en tête de fichier : DATABASE_URL doit déjà être définie.
    from app.db import Base, get_db
    from app.main import app

    # StaticPool : une seule connexion partagée. Sans cela, chaque thread (le TestClient
    # exécute l'application dans un autre thread) aurait sa propre base en mémoire, vide.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
