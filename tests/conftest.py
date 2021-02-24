from typing import Generator

import pytest
import requests
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch) -> None:
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    def stunted_post():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: stunted_post())

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("MEDIAHAVEN_USERNAME", "username")
    monkeypatch.setenv("MEDIAHAVEN_PASSWORD", "password")
    monkeypatch.setenv("MEDIAHAVEN_HOST", "host")
