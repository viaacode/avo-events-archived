#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Union
import pytest

from app.core.event_handler import (
    determine_original_item,
    determine_original_pid,
    get_original_pid_from_fragment,
)
from tests.resources import (
    fragment_info_json,
    query_result_multiple_results_json_3,
    query_result_multiple_results_json,
    query_result_no_result_json,
    query_result_single_result_json,
)

from mediahaven.mocks.base_resource import (
    MediaHavenSingleObjectJSONMock,
    MediaHavenPageObjectJSONMock,
)

test_data_original_pid = [
    # Regular pid
    ("639k36mb0j.mp4", "639k36mb0j"),
    # Regular pid with `mezanine`
    ("vx05x2t51z_mezanine.mp4", "vx05x2t51z_mezanine"),
    # Regular pid, exported more than once
    ("125q82jj84-1.mp4", "125q82jj84"),
    # Other valid forms
    ("930ns3cj88.mxf.zip", "930ns3cj88"),
    ("w37kq0rq6r_open.srt", "w37kq0rq6r_open"),
    ("p55dc0sg4r_wav.mp4", "p55dc0sg4r_wav"),
    ("p55dc0sg4r_wavelength.extension", "p55dc0sg4r_wavelength"),
    ("h98z89692m_twelvecharst-2.mp4", "h98z89692m_twelvecharst"),
    ("h98z89692m_mezanine-2.mp4", "h98z89692m_mezanine"),
    ("h98z89692m_mezzanine-2.mp4", "h98z89692m_mezzanine"),
    ("8911p0vh59_metadata.ebu", "8911p0vh59_metadata"),
    # Invalid export names
    ("2000-1.mp4", None),
    ("EXPERT_Voornaam Van Achternaam- Programma Naam.mp4", None),
    ("Essence pid tq5r813p56.mp4", None),
    ("een_random_string_met.extensie", None),
    ("TER ZAKE.mp4", None),
    # Typo in export name (starts with capital letter)
    ("Eb56d24nz3c.mp4", None),
]


@pytest.mark.parametrize("s3_object_key,expected_value", test_data_original_pid)
def test_determine_original_pid(s3_object_key: str, expected_value: Union[str, None]):
    # Act
    original_pid = determine_original_pid(s3_object_key)
    # Assert
    assert original_pid == expected_value


def test_get_original_pid_from_fragment_correct():
    # Arrange
    fragment = MediaHavenSingleObjectJSONMock(json.loads(fragment_info_json.decode()))
    # Act
    original_pid = get_original_pid_from_fragment(fragment)
    # Assert
    assert original_pid == "s3filename"


def test_get_original_pid_from_fragment_AttributeError():
    # Arrange
    fragment = MediaHavenSingleObjectJSONMock(json.loads(fragment_info_json.decode()))
    del fragment.Dynamic.s3_object_key
    # Act & assert
    with pytest.raises(AttributeError):
        _ = get_original_pid_from_fragment(fragment)


def test_get_original_pid_from_fragment_ValueError():
    # Arrange
    fragment = MediaHavenSingleObjectJSONMock(json.loads(fragment_info_json.decode()))
    fragment.Dynamic.s3_object_key = "a wrong export name"
    # Act & assert
    with pytest.raises(ValueError):
        _ = get_original_pid_from_fragment(fragment)


def test_determine_original_item_single_item():
    # Arrange
    mediahaven_result = MediaHavenPageObjectJSONMock(
        json.loads(query_result_single_result_json)["Results"],
        nr_of_results=1,
        total_nr_of_results=1,
    )
    # Act
    fragment_id = determine_original_item(mediahaven_result)
    # Assert
    assert (
        fragment_id
        == "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525"
    )


def test_determine_original_item_multiple_items_2():
    # Arrange
    mediahaven_result = MediaHavenPageObjectJSONMock(
        json.loads(query_result_multiple_results_json)["Results"],
        nr_of_results=2,
        total_nr_of_results=2,
    )
    # Act
    fragment_id = determine_original_item(mediahaven_result)
    # Assert
    assert (
        fragment_id
        == "1234567891011121314151617181920212223242526272829303132333435363dfe24b95373a4ca6b00ebfee3447bd75"
    )


def test_determine_original_item_multiple_items_3():
    # Arrange
    mediahaven_result = MediaHavenPageObjectJSONMock(
        json.loads(query_result_multiple_results_json_3)["Results"],
        nr_of_results=3,
        total_nr_of_results=3,
    )
    # Act
    fragment_id = determine_original_item(mediahaven_result)
    # Assert
    assert (
        fragment_id
        == "911590738667861623378452998032598893744975670506425831782315371606163411184739903652215505881300"
    )
