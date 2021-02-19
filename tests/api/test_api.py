import json

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from tests.resources import (
    fragment_info,
    query_result_single_result,
    single_premis_event,
)


def test_handle_events(client: TestClient, mocker: MockerFixture) -> None:
    mocker.patch(
        "app.services.mediahaven.MediahavenService.get_fragment",
        return_value=json.loads(fragment_info.decode()),
    )
    mocker.patch(
        "app.services.mediahaven.MediahavenService.query",
        return_value=query_result_single_result,
    )
    mocker.patch(
        "app.services.mediahaven.MediahavenService.update_metadata",
        return_value=True,
    )

    response = client.post(
        "/event/",
        data=single_premis_event,
    )

    assert response.status_code == 202
    content = response.json()
    assert "Updating" in content["message"]
