"""Configuration commune des tests."""

import os

# Doit être défini AVANT l'import de l'app : app.db crée le moteur à l'import.
# SQLite en mémoire : les tests unitaires n'ont pas besoin de PostgreSQL.
os.environ.setdefault("DATABASE_URL", "sqlite://")
