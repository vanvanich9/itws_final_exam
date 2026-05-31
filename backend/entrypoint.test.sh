#!/bin/sh
set -e

echo '==> Check code style'
poetry run ruff check core src tests

echo '==> Run unit tests'
poetry run pytest tests/unit

echo '==> Run integration tests'
poetry run pytest tests/integration
