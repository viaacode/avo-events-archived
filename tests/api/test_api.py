import json

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from tests.resources import (
    fragment_info,
    query_result_single_result,
    sidecar,
    single_premis_event,
    single_premis_event_nok,
)


def test_handle_events(client: TestClient, mocker: MockerFixture) -> None:
    get_fragment_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.get_fragment",
        return_value=json.loads(fragment_info.decode()),
    )
    query_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.query",
        return_value=query_result_single_result,
    )
    update_metadata_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.update_metadata",
        return_value=True,
    )

    response = client.post(
        "/event/",
        data=single_premis_event,
    )

    get_fragment_mock.assert_called_once_with("a1b2c3")
    query_mock.assert_called_once_with([("PID", "s3_filename")])
    update_metadata_mock.assert_called_once_with(
        "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525",
        sidecar,
    )
    assert response.status_code == 202
    content = response.json()
    assert "Updating 1" in content["message"]


def test_handle_NOK_events(client: TestClient, mocker: MockerFixture) -> None:
    get_fragment_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.get_fragment",
        return_value=json.loads(fragment_info.decode()),
    )
    query_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.query",
        return_value=query_result_single_result,
    )
    update_metadata_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.update_metadata",
        return_value=True,
    )

    response = client.post(
        "/event/",
        data=single_premis_event_nok,
    )

    get_fragment_mock.assert_not_called()
    query_mock.assert_not_called()
    update_metadata_mock.assert_not_called()
    assert response.status_code == 202
    content = response.json()
    assert "Updating 0" in content["message"]
