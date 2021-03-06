#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from lxml.etree import XMLSyntaxError
from lxml.etree import fromstring as parse_xml_string

from app.core.events_parser import _get_xpath_from_event, parse_premis_events
from tests.resources import (
    invalid_xml_event,
    multi_premis_event,
    single_event_no_external_id,
    single_premis_event,
    single_premis_event_archived_on_disk,
    single_premis_event_nok,
)


@pytest.mark.parametrize(
    "resource, event_type",
    [
        (
            single_premis_event,
            "FLOW.ARCHIVED",
        ),
        (
            single_premis_event_archived_on_disk,
            "RECORDS.FLOW.ARCHIVED_ON_DISK",
        ),
    ],
)
def test_single_event(resource, event_type):
    p = parse_premis_events(resource)
    assert len(p["events"]) == 1
    assert p["events"][0]["event_id"] == "111"
    assert p["events"][0]["event_detail"] == "Ionic Defibulizer"
    assert p["events"][0]["mediahaven_id"] == "a1b2c3"
    assert p["events"][0]["event_type"] == event_type
    assert p["events"][0]["event_outcome"] == "OK"
    assert p["events"][0]["event_datetime"] == "2019-03-30T05:28:40Z"
    assert p["events"][0]["external_id"] == "a1"
    assert p["events"][0]["is_valid"]
    assert p["events"][0]["has_valid_outcome"]


def test_single_event_nok():
    p = parse_premis_events(single_premis_event_nok)
    assert len(p["events"]) == 1
    assert p["events"][0]["is_valid"]
    assert not p["events"][0]["has_valid_outcome"]


def test_multi_event():
    p = parse_premis_events(multi_premis_event)
    assert len(p["events"]) == 3
    assert p["events"][0]["event_id"] == "222"
    assert p["events"][0]["event_detail"] == "Ionic Defibulizer Plus"
    assert p["events"][0]["mediahaven_id"] == "a1b2c3"
    assert p["events"][0]["event_type"] == "EXPORT"
    assert p["events"][0]["event_outcome"] == "OK"
    assert p["events"][0]["event_datetime"] == "2020-03-30T05:28:40Z"
    assert p["events"][0]["has_valid_outcome"]
    assert not p["events"][0]["is_valid"]

    assert p["events"][1]["event_id"] == "333"
    assert p["events"][1]["event_detail"] == "Ionic Defibulizer"
    assert p["events"][1]["mediahaven_id"] == "d4e5f6"
    assert p["events"][1]["event_type"] == "FLOW.ARCHIVED"
    assert p["events"][1]["event_outcome"] == "OK"
    assert p["events"][1]["event_datetime"] == "2019-03-30T05:28:40Z"
    assert p["events"][1]["has_valid_outcome"]
    assert p["events"][1]["is_valid"]

    assert p["events"][2]["event_id"] == "444"
    assert p["events"][2]["event_detail"] == "Ionic Defibulizer 2"
    assert p["events"][2]["mediahaven_id"] == "g7h8j9"
    assert p["events"][2]["event_type"] == "RECORDS.FLOW.ARCHIVED"
    assert p["events"][2]["event_outcome"] == "OK"
    assert p["events"][2]["event_datetime"] == "2019-03-30T05:28:40Z"
    assert p["events"][2]["has_valid_outcome"]
    assert p["events"][2]["is_valid"]


def test_invalid_xml_event():
    with pytest.raises(XMLSyntaxError):
        parse_premis_events(invalid_xml_event)


def test_single_event_no_external_id():
    p = parse_premis_events(single_event_no_external_id)
    assert len(p["events"]) == 1

    assert p["events"][0]["is_valid"]
    assert not p["events"][0]["has_valid_outcome"]
    assert not p["events"][0]["external_id"]


def test_get_xpath_from_event():
    input_xml = "<xml><path>value</path></xml>"
    tree = parse_xml_string(input_xml)
    assert _get_xpath_from_event(tree, "no_such_path") == ""
    assert _get_xpath_from_event(tree, "path") == "value"
