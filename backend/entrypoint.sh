#!/bin/sh
set -e

APP_MODULE="${APP_MODULE:-src.asgi:app}"
WORKER_CLASS="${WORKER_CLASS:-uvicorn.workers.UvicornWorker}"
BIND="${BIND:-0.0.0.0:8000}"

exec gunicorn "${APP_MODULE}" \
  -k "${WORKER_CLASS}" \
  --bind "${BIND}" \
  --workers "${GUNICORN_WORKERS:-4}"
