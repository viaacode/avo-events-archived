.ONESHELL:
SHELL = /bin/bash

.PHONY: all test

test:
	pip3 install -r requirements.txt -r requirements-dev.txt --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be
	export $(shell cat .env.example | xargs)
	python -m  pytest -vvv --cov=./app --junit-xml=./tests/test_results.xml