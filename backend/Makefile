.PHONY: fmt lint

fmt:
	@poetry run ruff format src

lint: fmt
	@poetry run ruff check src --fix