NAME := avo-events-archived

PYTHON_FILES := main.py ./app/ ./tests/
VENV_NAME=.venv
VENV_PYTHON=${VENV_NAME}/bin/python
VENV_ACTIVATE=. ${VENV_NAME}/bin/activate

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available make commands:"
	@echo ""
	@echo "  init        make a virtual environment and install dependencies"
	@echo "  init-dev    make a virtual environment and install dependencies including development dependencies"
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
	$(info    "INFO: Initialising virtual environment and installed dependencies in $(VENV_NAME)")
	python3 -m venv ${VENV_NAME}
	${VENV_PYTHON} -m pip install -r requirements.txt \
	    --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple \
	    --trusted-host do-prd-mvn-01.do.viaa.be

.PHONY: init-dev
init-dev:
	make init
	${VENV_PYTHON} -m pip install -r requirements-dev.txt

.PHONY: clean
clean:
	$(info    "INFO: Cleaning $(VENV_NAME)")
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf .coverage .mypy_cache .pytest_cache ${VENV_NAME}

.PHONY: lint
lint:
	${VENV_ACTIVATE}; isort --profile=black --check-only $(PYTHON_FILES) || true
	${VENV_ACTIVATE}; black --check --diff $(PYTHON_FILES) || true
	${VENV_ACTIVATE}; flake8 $(PYTHON_FILES) || true
	${VENV_ACTIVATE}; mypy --ignore-missing-imports $(PYTHON_FILES) || true

.PHONY: format
format:
	isort --profile=black --force-single-line-imports $(PYTHON_FILES)
	autoflake -r -i --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports $(PYTHON_FILES)
	isort --profile=black $(PYTHON_FILES)
	black $(PYTHON_FILES)


.PHONY: test
test:
ifneq ("$(wildcard .env)", ".env")
	cp .env.example .env
endif
	export $$(grep -v '^#' .env | xargs -d '\n') && ${VENV_ACTIVATE} && pytest -vvv

.PHONY: run
run:
ifneq ("$(wildcard .env)", ".env")
	@echo "No .env file found."
else
	export $$(grep -v '^#' .env | xargs -d '\n') && ${VENV_ACTIVATE} && python main.py
endif
