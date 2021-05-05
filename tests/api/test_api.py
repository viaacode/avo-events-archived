import json

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from unittest.mock import call

from tests.resources import (
    fragment_info_json,
    fragment_info_xml,
    query_result_single_result_json,
    query_result_multiple_results_json,
    sidecar,
    single_premis_event,
    single_premis_event_empty_detail,
    single_premis_event_nok,
)


@pytest.mark.parametrize(
    "resource",
    [
        single_premis_event,
        single_premis_event_empty_detail,
    ],
)
def test_handle_events(client: TestClient, mocker: MockerFixture, resource) -> None:
    def get_fragment_side_effect(fragment_id, content_type = "json"):
        if content_type == "json":
            return json.loads(fragment_info_json.decode())
        if content_type == "xml":
            return fragment_info_xml
        return ""

    get_fragment_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.get_fragment",
        side_effect=get_fragment_side_effect,
    )
    query_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.query",
        return_value=json.loads(query_result_single_result_json),
    )
    update_metadata_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.update_metadata",
        return_value=True,
    )

    response = client.post(
        "/event/",
        data=resource,
    )
    get_fragment_mock.assert_has_calls(
        [
            call("a1b2c3"),
            call(
                "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525",
                "xml",
            ),
        ]
    )
    query_mock.assert_called_once_with([("PID", "s3_filename")])
    update_metadata_mock.assert_called_once_with(
        "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525",
        sidecar,
    )
    assert response.status_code == 202
    content = response.json()
    assert "Updating 1" in content["message"]

@pytest.mark.parametrize(
    "resource",
    [
        single_premis_event,
        single_premis_event_empty_detail,
    ],
)
def test_handle_events_multiple_results_for_pid(client: TestClient, mocker: MockerFixture, resource) -> None:
    def get_fragment_side_effect(fragment_id, content_type = "json"):
        if content_type == "json":
            return json.loads(fragment_info_json.decode())
        if content_type == "xml":
            return fragment_info_xml
        return ""

    get_fragment_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.get_fragment",
        side_effect=get_fragment_side_effect,
    )
    query_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.query",
        return_value=json.loads(query_result_multiple_results_json),
    )
    update_metadata_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.update_metadata",
        return_value=True,
    )

    response = client.post(
        "/event/",
        data=resource,
    )
    get_fragment_mock.assert_has_calls(
        [
            call("a1b2c3"),
            call(
                "1234567891011121314151617181920212223242526272829303132333435363dfe24b95373a4ca6b00ebfee3447bd75",
                "xml",
            ),
        ]
    )
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
        return_value=json.loads(fragment_info_json.decode()),
    )
    query_mock = mocker.patch(
        "app.services.mediahaven.MediahavenService.query",
        return_value=query_result_single_result_json,
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
