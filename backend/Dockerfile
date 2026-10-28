# Image de production de l'API FastAPI — build multi-stage.
# Étape 1 (builder) : installe les dépendances dans un venv.
# Étape 2 (runtime) : image vierge qui ne reçoit que le venv et le code,
#   donc plus petite et sans outils de build (moins de surface d'attaque).

# ---------- Étape 1 : builder ----------
FROM python:3.12-slim AS builder

# Pas de cache pip dans l'image, pas de message de mise à jour de pip.
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# requirements.txt copié SEUL avant le code : tant que les dépendances ne changent
# pas, Docker réutilise cette couche en cache (un changement de code ne relance pas pip).
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Étape 2 : runtime ----------
FROM python:3.12-slim AS runtime

# PYTHONDONTWRITEBYTECODE : pas de .pyc inutiles ; PYTHONUNBUFFERED : logs visibles
# immédiatement dans `docker logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Utilisateur non-root, sans shell ni répertoire personnel : si l'app est compromise,
# l'attaquant n'est pas root dans le conteneur.
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# On ne récupère que le venv construit (sans pip ni cache de build) et le code.
COPY --from=builder /opt/venv /opt/venv
COPY app ./app

USER app

EXPOSE 8000

# L'image slim n'a ni curl ni wget : on utilise urllib (bibliothèque standard).
# Une réponse 503 (base injoignable) lève une exception -> code retour 1 -> "unhealthy".
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"]

# Forme "exec" : uvicorn est le processus principal (PID 1) et reçoit SIGTERM
# directement, donc l'arrêt du conteneur est propre.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
