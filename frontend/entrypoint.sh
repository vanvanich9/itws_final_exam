#!/bin/sh
set -e

if [ "$DOCKER_ENV" = "dev" ]; then
	npm run build
fi

exec node build
