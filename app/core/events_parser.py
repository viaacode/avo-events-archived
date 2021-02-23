#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import BytesIO

from lxml import etree

# Constants
PREMIS_NAMESPACE = "info:lc/xmlns/premis-v2"

VALID_EVENT_TYPES = [
    "FLOW.ARCHIVED",
    "RECORDS.FLOW.ARCHIVED",
    "RECORDS.FLOW.ARCHIVED_ON_DISK",
]
VALID_OUTCOME = "OK"

XPATHS = {
    "event_type": "./p:eventType",
    "event_datetime": "./p:eventDateTime",
    "event_detail": "./p:eventDetail",
    "event_id": "./p:eventIdentifier[p:eventIdentifierType='MEDIAHAVEN_EVENT']/p:eventIdentifierValue",
    "event_outcome": "./p:eventOutcomeInformation/p:eventOutcome",
    "fragment_id": "./p:linkingObjectIdentifier[p:linkingObjectIdentifierType='MEDIAHAVEN_ID']/p:linkingObjectIdentifierValue",
    "external_id": "./p:linkingObjectIdentifier[p:linkingObjectIdentifierType='EXTERNAL_ID']/p:linkingObjectIdentifierValue",
}


def parse_premis_events(input_xml: bytes):
    tree = etree.parse(BytesIO(input_xml))

    elements = tree.xpath("/events/p:event", namespaces={"p": PREMIS_NAMESPACE})

    events = [
        event
        for event in (parse_premis_event(element) for element in elements)
        if event["is_valid"] and event["has_valid_outcome"]
    ]

    return {"events": events}


def parse_premis_event(element):
    return {
        "event_type": _get_xpath_from_event(element, XPATHS["event_type"]),
        "event_datetime": _get_xpath_from_event(element, XPATHS["event_datetime"]),
        "event_detail": _get_xpath_from_event(element, XPATHS["event_detail"]),
        "event_id": _get_xpath_from_event(element, XPATHS["event_id"]),
        "event_outcome": _get_xpath_from_event(element, XPATHS["event_outcome"]),
        "fragment_id": _get_xpath_from_event(element, XPATHS["fragment_id"]),
        "external_id": _get_xpath_from_event(element, XPATHS["external_id"]),
        "is_valid": _is_valid(_get_xpath_from_event(element, XPATHS["event_type"])),
        "has_valid_outcome": _has_valid_outcome(
            _get_xpath_from_event(element, XPATHS["event_outcome"])
        ),
    }


def _get_xpath_from_event(element, xpath: str) -> str:
    """Parses based on an xpath, returns empty string if absent"""
    try:
        return element.xpath(xpath, namespaces={"p": PREMIS_NAMESPACE})[0].text
    except IndexError:
        return ""


def _is_valid(event_type: str):
    """A PremisEvent is valid only if:
    - it has a valid eventType for this particular application,
    - if it has a fragment ID.
    """
    if event_type in VALID_EVENT_TYPES:
        return True
    return False


def _has_valid_outcome(event_outcome: str):
    """Check if the outcome of the event was successful"""
    return event_outcome == VALID_OUTCOME
