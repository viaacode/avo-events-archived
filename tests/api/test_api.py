import json

import pytest
from fastapi.testclient import TestClient
from unittest.mock import call, patch
from mediahaven.mediahaven import AcceptFormat, ContentType
from mediahaven.mocks.base_resource import (
    MediaHavenPageObjectJSONMock,
    MediaHavenSingleObjectJSONMock,
    MediaHavenSingleObjectXMLMock,
)

from app.app import app
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
@patch("app.app.MediaHaven")
@patch("app.app.ROPCGrant")
def test_handle_events(
    ropc_grant_mock,
    media_haven_mock,
    resource,
) -> None:
    media_haven_mock().records.get.side_effect = [
        MediaHavenSingleObjectJSONMock(json.loads(fragment_info_json.decode())),
        MediaHavenSingleObjectXMLMock(fragment_info_xml.decode("UTF-8")),
    ]

    media_haven_mock().records.search.return_value = MediaHavenPageObjectJSONMock(
        json.loads(query_result_single_result_json)["Results"]
    )
    media_haven_mock().records.update.return_value = True

    with TestClient(app) as client:
        response = client.post(
            "/event/",
            data=resource,
        )

    media_haven_mock().records.get.assert_has_calls(
        [
            call("a1b2c3"),
            call(
                "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525",
                accept_format=AcceptFormat.XML,
            ),
        ]
    )
    media_haven_mock().records.search.assert_called_once_with(q="+PID:s3filename")
    media_haven_mock().records.update.assert_called_once_with(
        "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525",
        metadata=sidecar,
        metadata_content_type=ContentType.XML.value,
        reason="[avo-events-handler] Update item with original metadata",
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
@patch("app.app.MediaHaven")
@patch("app.app.ROPCGrant")
def test_handle_events_multiple_results_for_pid(
    ropc_grant_mock,
    media_haven_mock,
    resource,
) -> None:
    media_haven_mock().records.get.side_effect = [
        MediaHavenSingleObjectJSONMock(json.loads(fragment_info_json.decode())),
        MediaHavenSingleObjectXMLMock(fragment_info_xml.decode("UTF-8")),
    ]

    media_haven_mock().records.search.return_value = MediaHavenPageObjectJSONMock(
        json.loads(query_result_multiple_results_json)["Results"],
        total_nr_of_results=2,
        nr_of_results=2,
    )
    media_haven_mock().records.update.return_value = True

    with TestClient(app) as client:
        response = client.post(
            "/event/",
            data=resource,
        )

    media_haven_mock().records.get.assert_has_calls(
        [
            call("a1b2c3"),
            call(
                "1234567891011121314151617181920212223242526272829303132333435363dfe24b95373a4ca6b00ebfee3447bd75",
                accept_format=AcceptFormat.XML,
            ),
        ]
    )
    media_haven_mock().records.search.assert_called_once_with(q="+PID:s3filename")
    media_haven_mock().records.update.assert_called_once_with(
        "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525",
        metadata=sidecar,
        metadata_content_type=ContentType.XML.value,
        reason="[avo-events-handler] Update item with original metadata",
    )
    assert response.status_code == 202
    content = response.json()
    assert "Updating 1" in content["message"]


@patch("app.app.MediaHaven")
@patch("app.app.ROPCGrant")
def test_handle_NOK_events(
    ropc_grant_mock,
    media_haven_mock,
) -> None:
    with TestClient(app) as client:
        response = client.post(
            "/event/",
            data=single_premis_event_nok,
        )
    media_haven_mock().records.get.assert_not_called()
    media_haven_mock().records.search.assert_not_called()
    media_haven_mock().records.update.assert_not_called()
    assert response.status_code == 202
    content = response.json()
    assert "Updating 0" in content["message"]
