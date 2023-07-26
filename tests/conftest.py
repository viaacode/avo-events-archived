import pytest
import requests


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch) -> None:
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    def stunted_post():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: stunted_post())
