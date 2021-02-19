NAME := avo-events-archived
POETRY := $(shell command -v poetry 2> /dev/null)
FOLDERS := ./app/ ./tests/

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available make commands:"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo "  clean       remove all temporary files"
	@echo "  lint        run the code linters"
	@echo "  format      reformat code"
	@echo "  test        run all the tests"
	@echo "  run         start uvicorn development server"
	@echo ""

.PHONY: install
install:
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf .coverage .mypy_cache

.PHONY: lint
lint:
	$(POETRY) run isort --profile=black --check-only $(FOLDERS)
	$(POETRY) run black --check $(FOLDERS) --diff
	$(POETRY) run flake8 $(FOLDERS)
	$(POETRY) run mypy $(FOLDERS) --ignore-missing-imports
	$(POETRY) run bandit -r $(FOLDERS) -s B608

.PHONY: format
format:
	$(POETRY) run isort --profile=black --force-single-line-imports $(FOLDERS)
	$(POETRY) run autoflake -r -i --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports $(FOLDERS)
	$(POETRY) run isort --profile=black $(FOLDERS)
	$(POETRY) run black $(FOLDERS)


.PHONY: test
test:
	$(POETRY) run pytest ./tests/ --cov-report term-missing --cov-fail-under 100 --cov ./app/

.PHONY: run
run:
	$(POETRY) run uvicorn app.main:app --reload