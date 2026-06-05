.PHONY: fmt lint test

fmt:
	npm run fmt

lint: fmt
	npm run lint

test:
	docker compose -f docker-compose.test.yml up --build --exit-code-from tests tests
