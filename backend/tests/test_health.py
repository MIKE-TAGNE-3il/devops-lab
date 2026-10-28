from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db import get_db
from app.main import app

client = TestClient(app)


def test_health_ok():
    reponse = client.get("/api/health")

    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok", "database": "ok"}


def test_health_base_injoignable(caplog):
    # On remplace la session par une fausse session dont la base est en panne.
    class SessionEnPanne:
        def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("connexion refusée"))

    app.dependency_overrides[get_db] = lambda: SessionEnPanne()
    try:
        reponse = client.get("/api/health")
    finally:
        app.dependency_overrides.clear()

    assert reponse.status_code == 503
    assert reponse.json()["database"] == "unreachable"
    # La cause de la panne doit être écrite dans les logs, pas seulement renvoyée en 503.
    assert "base de données injoignable" in caplog.text
    assert "connexion refusée" in caplog.text
