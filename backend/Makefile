.PHONY: fmt lint test

fmt:
	@poetry run ruff format src tests core

lint: fmt
	@poetry run ruff check src tests core --fix

test:
	docker compose -f docker-compose.test.yml up --build --exit-code-from tests tests
