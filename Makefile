.PHONY: lint test

lint:
	ruff check .
	black --check .
	isort --check .
	mypy .

test:
	pytest tests/ -v

install:
	pip install ruff black isort mypy pytest pytest-odoo

