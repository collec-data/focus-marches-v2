# Stage 1: récupération des dépendances dans un .venv
FROM ghcr.io/astral-sh/uv:0.12.23-python3.14-alpine3.23@sha256:5bad981cb914722a38eb1f9de538194f14d03c5f104d3b30f19239327d57eb50 AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN apk add --no-cache build-base curl mariadb mariadb-dev

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --locked --no-editable --no-install-project

# Stage 2: image de déploiement
FROM python:3.14.8-alpine3.23@sha256:e7cff362a12454395f8dc99607c21a602ea880cdce03538877b90c2ba932b16f
EXPOSE 80
WORKDIR /app

RUN apk add --no-cache build-base curl mariadb mariadb-dev

# Copie du .venv
COPY --from=builder /app/.venv /app/.venv

# Copie des sources
COPY ./app /app/app
COPY ./cpv_2008_fr.csv /app/cpv_2008_fr.csv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80" ]
