# AvO Events Archived

## Synopsis

When an item is archived for AvO it needs to be updated with the metadata from the original fragment.
This service queries MediaHaven for the original metdata and updates the new item after a small transformation.

## Prerequisites

- Git
- Docker (optional)
- Python 3.6+
- Access to the [meemoo PyPi](http://do-prd-mvn-01.do.viaa.be:8081)
- Poetry

## Usage

### Running locally

1. Clone this repository
2. `cd` into the new directory
3. `poetry install`
4. `poetry run uvicorn app.main:app`
5. `http://127.0.0.1:8000/health/live` should return `OK`

### Running tests

After cloning and installing the tests can be run with `poetry run pytest -v`
