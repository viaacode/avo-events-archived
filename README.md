# AvO Events Archived

## Synopsis

When an item is archived for AvO it needs to be updated with the metadata from the original fragment.
This service queries MediaHaven for the original metdata and updates the new item after a small transformation.

## Prerequisites

- Git
- Docker (optional)
- Python 3.7+
- Access to the [meemoo PyPi](http://do-prd-mvn-01.do.viaa.be:8081)

## Usage

### Running locally

#### Using Makefile

1. Clone this repository.
2. `cd` into the new directory .
3. Run `make init` to initialize the virtual environment and install dependencies.
4. Edit the `.env` file if needed.
5. Run `make run` to start the application.
6. `http://127.0.0.1:8080/health/live` should return `OK`.

#### Manual

1. Clone this repository.
2. `cd` into the new directory.
3. Make a new virtual environment using `python3 -m venv env`.
4. Activate the new environment using `source env/bin/activate`.
5. Install dependencies using `pip install -r requirements.txt`.
6. Set environment variables (all variables in `.env.example` have to be set).
7. Start the application with `python main.py`.
8. `http://127.0.0.1:8080/health/live` should return `OK`.

#### Docker

1. Clone this repository.
2. `cd` into the new directory.
3. Build the Docker container using `docker build -t avo-events-archived .`.
4. Make a `.env`-file, you can rename `.env.example` and fill in correct values.
5. Run the container using `docker run --env-file .env -p 8080:8080 avo-events-archived:latest`.
6. `http://127.0.0.1:8080/health/live` should return `OK`.

### Running tests

Assuming you have already cloned the repository and are in the project folder.

#### Using Makefile

1. Run `make init-dev` to install dev dependencies.
2. Run `make test` to run the tests.

#### Manual

1. Activate your virtual environment using `source env/bin/activate`.
2. Install development dependencies using `pip install -r requirements-dev.txt`.
3. Set environment variables (all variables in `.env.example` have to be set, but these can be dummy variables).
4. Run the tests using `pytest`

#### Docker

1. Build the Docker container using `docker build -t avo-events-archived .`.
2. Run the tests in the container using `docker container run --name aea_test --env-file .env --entrypoint python avo-events-archived:latest "-m" "pytest"`.
3. Clean up after yourself and remove the container using `docker rm aea_test`.