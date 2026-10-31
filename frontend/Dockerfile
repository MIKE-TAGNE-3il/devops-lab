# Image de production du frontend React — build multi-stage.
# Étape 1 (build)   : Node compile l'application en fichiers statiques (dossier dist/).
# Étape 2 (runtime) : Nginx non-root ne reçoit que dist/ : plus de Node, de code source
#   ni de node_modules, donc une image petite et peu exposée.

# ---------- Étape 1 : build ----------
# Node 24 : Node 20 est en fin de vie depuis le 30/04/2026 (plus de correctifs de sécurité).
FROM node:24-alpine AS build

WORKDIR /app

# package*.json copiés SEULS avant le code : tant que les dépendances ne changent pas,
# Docker réutilise la couche "npm ci" en cache.
# npm ci (et non npm install) : installe exactement les versions du lockfile, et échoue
# si package.json et package-lock.json ne sont pas d'accord.
COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.js ./
COPY src ./src
RUN npm run build

# ---------- Étape 2 : runtime ----------
# nginx-unprivileged : image officielle de Nginx qui tourne sans être root et écoute sur
# le port 8080 (un utilisateur non-root ne peut pas ouvrir un port inférieur à 1024).
# 1.30 = branche stable de Nginx (les versions paires sont les stables).
FROM nginxinc/nginx-unprivileged:1.30-alpine AS runtime

# Applique les correctifs de sécurité Alpine publiés depuis la construction de l'image de base
# (le scan Trivy de la CI échoue sur toute faille HIGH/CRITICAL qui a un correctif). Il faut
# être root pour installer des paquets : on y passe le temps de la mise à jour, puis on revient
# à l'utilisateur 101 (nginx) de l'image de base, donc l'image finale reste NON-ROOT.
# --no-cache : l'index des paquets n'est pas conservé dans l'image.
USER root
RUN apk upgrade --no-cache
USER 101

# Notre configuration remplace celle par défaut.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Seul résultat du build : les fichiers statiques.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

# wget existe dans l'image alpine (busybox) : pas besoin d'installer curl.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["wget", "-q", "--spider", "http://127.0.0.1:8080/"]
