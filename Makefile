.PHONY: lint lint-fix test-focused test-focused-update test-docker install pre-commit

MODULE ?= academy_management

lint:
	ruff check .
	black --check .
	isort --check .
	mypy .

lint-fix:
	ruff check . --fix
	black .
	isort .

# Run only the named test files against the existing database. This avoids both
# the full suite and the module update, so it is the fastest feedback loop for
# Python-only changes.
# Usage: make test-focused FILES="test_attendance.py test_student_models.py"
#        make test-focused MODULE=academy_catalog FILES="test_catalog_course.py"
test-focused:
	@test -n "$(FILES)" || (echo 'Usage: make test-focused FILES="test_file.py ..."'; exit 1)
	@status=0; for file in $(FILES); do \
		docker compose exec odoo odoo -d odoo_test \
		  --test-file=/mnt/extra-addons/$(MODULE)/tests/$$file \
		  --stop-after-init --http-port=8099 || status=1; \
	done; exit $$status

# Use this when the change also updates module data, views, security records,
# or database schema. It still runs only the requested test files.
# Usage: make test-focused-update FILES="test_security.py"
test-focused-update:
	@test -n "$(FILES)" || (echo 'Usage: make test-focused-update FILES="test_file.py ..."'; exit 1)
	@status=0; for file in $(FILES); do \
		docker compose exec odoo odoo -d odoo_test -u $(MODULE) \
		  --test-file=/mnt/extra-addons/$(MODULE)/tests/$$file \
		  --stop-after-init --http-port=8099 || status=1; \
	done; exit $$status

test-docker:
	@echo "Creating fresh test database..."
	docker compose exec db psql -U odoo -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='odoo_test';"
	docker compose exec db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo_test;"
	docker compose exec db psql -U odoo -d postgres -c "CREATE DATABASE odoo_test OWNER odoo;"
	@echo "Running Odoo tests..."
	docker compose exec odoo odoo -d odoo_test --test-enable --test-tags /academy_management --stop-after-init --init=academy_management --http-port=8099

install:
	pip install -r requirements-test.txt

pre-commit:
	pre-commit install
	pre-commit run --all-files
