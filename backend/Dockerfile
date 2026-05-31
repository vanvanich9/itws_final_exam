# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

RUN pip install --no-cache-dir poetry

COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

FROM base AS dev

ENV DOCKER_ENV=dev

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

FROM base AS prod

ENV DOCKER_ENV=prod

COPY core/ ./core/
COPY src/ ./src/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
