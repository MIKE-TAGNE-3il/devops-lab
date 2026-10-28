"""Configuration de l'application, lue depuis les variables d'environnement."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Aucune valeur par défaut : si DATABASE_URL est absente, l'app refuse de démarrer
    # plutôt que de se connecter à une base inattendue.
    database_url: str


@lru_cache
def get_settings() -> Settings:
    # Mise en cache : l'environnement n'est lu qu'une seule fois.
    return Settings()
