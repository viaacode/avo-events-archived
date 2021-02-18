import json

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from app.services.mediahaven import MediahavenService
from tests.resources import (
    fragment_info,
    invalid_premis_event,
    invalid_xml_event,
    multi_premis_event,
    query_result_single_result,
    single_event_no_external_id,
    single_premis_event,
    single_premis_event_archived_on_disk,
    single_premis_event_nok,
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
        f"/event/",
        data=single_premis_event,
    )

    assert response.status_code == 202
    content = response.json()
    assert "Updating" in content["message"]
