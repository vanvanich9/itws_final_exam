.PHONY: fmt lint test \
	fmt-backend fmt-frontend \
	lint-backend lint-frontend \
	test-backend test-frontend

# ── All projects ───────────────────────────────────────────────────────────────

fmt: fmt-backend fmt-frontend

lint: lint-backend lint-frontend

test: test-backend test-frontend

# ── Backend ────────────────────────────────────────────────────────────────────

fmt-backend:
	@$(MAKE) -C backend fmt

lint-backend:
	@$(MAKE) -C backend lint

test-backend:
	@$(MAKE) -C backend test

# ── Frontend ───────────────────────────────────────────────────────────────────

fmt-frontend:
	@$(MAKE) -C frontend fmt

lint-frontend:
	@$(MAKE) -C frontend lint

test-frontend:
	@$(MAKE) -C frontend test
