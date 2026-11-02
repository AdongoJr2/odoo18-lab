.PHONY: lint lint-fix test test-docker install pre-commit

lint:
	ruff check .
	black --check .
	isort --check .
	mypy .

lint-fix:
	ruff check . --fix
	black .
	isort .

test:
	@echo "Run tests with Odoo (requires Odoo installation):"
	@echo "  odoo -d odoo_test --test-enable --stop-after-init --init=academy_management --http-port=8099"

test-docker:
	@echo "Creating fresh test database..."
	docker compose exec db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo_test;"
	docker compose exec db psql -U odoo -d postgres -c "CREATE DATABASE odoo_test OWNER odoo;"
	@echo "Running Odoo tests..."
	docker compose exec odoo odoo -d odoo_test --test-enable --stop-after-init --init=academy_management --http-port=8099

install:
	pip install -r requirements-test.txt

pre-commit:
	pre-commit install
	pre-commit run --all-files
