NAME := avo-events-archived

PYTHON_FILES := main.py ./app/ ./tests/
VENV_NAME=env
VENV_PYTHON=${VENV_NAME}/bin/python3
VENV_ACTIVATE=. ${VENV_NAME}/bin/activate
DEV_DEPENDENCIES_INSTALLED:=$(shell env/bin/pip list | grep -i 'isort' | wc -l)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available make commands:"
	@echo ""
	@echo "  init     make a virtual environment and install dependencies"
	@echo "  init-dev make a virtual environment and install dependencies including development dependencies"
	@echo "  clean       remove all temporary files and the virtual environment"
	@echo "  lint        run the code linters"
	@echo "  format      reformat code"
	@echo "  test        run all the tests"
	@echo "  run         start uvicorn development server"
	@echo ""

.PHONY: init
init:
ifneq ("$(wildcard .env)", ".env")
	cp .env.example .env
endif
	python3 -m venv env
	${VENV_PYTHON} -m pip install -r requirements.txt

.PHONY: init-dev
init-dev:
	make init
	${VENV_PYTHON} -m pip install -r requirements-dev.txt


.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf .coverage .mypy_cache .pytest_cache env

.PHONY: lint
lint:
	isort --profile=black --check-only $(PYTHON_FILES)
	black --check $(PYTHON_FILES) --diff
	flake8 $(PYTHON_FILES)
	mypy $(PYTHON_FILES) --ignore-missing-imports

.PHONY: format
format:
	isort --profile=black --force-single-line-imports $(PYTHON_FILES)
	autoflake -r -i --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports $(PYTHON_FILES)
	isort --profile=black $(PYTHON_FILES)
	black $(PYTHON_FILES)


.PHONY: test
test:
	export $$(grep -v '^#' .env | xargs -d '\n') && ${VENV_ACTIVATE} && pytest -vvv

.PHONY: run
run:
	export $$(grep -v '^#' .env | xargs -d '\n') && ${VENV_ACTIVATE} && python main.py