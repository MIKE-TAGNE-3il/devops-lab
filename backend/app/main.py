"""Point d'entrée de l'API FastAPI."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db

logger = logging.getLogger(__name__)

# Traefik route app.domaine.com/api vers ce service SANS retirer le préfixe :
# toutes les routes (y compris la doc) doivent donc vivre sous /api.
app = FastAPI(
    title="DevOps Lab API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

router = APIRouter(prefix="/api")


@router.get("/health")
def health(
    response: Response, db: Annotated[Session, Depends(get_db)]
) -> dict[str, str]:
    """Santé de l'API : 200 si PostgreSQL répond, 503 sinon.

    Utilisé par le HEALTHCHECK Docker et par Traefik pour écarter un conteneur défaillant.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as erreur:
        # Une seule ligne (pas de trace complète) : le healthcheck tourne toutes les 30 s,
        # une trace à chaque passage noierait les logs. La cause reste lisible avec
        # `docker compose logs backend`.
        logger.error("Healthcheck : base de données injoignable (%s)", erreur)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "database": "unreachable"}
    return {"status": "ok", "database": "ok"}


app.include_router(router)
