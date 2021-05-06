#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pytest

from app.core.event_handler import determine_original_item
from tests.resources import (
    fragment_info_json,
    query_result_multiple_results_json_3,
    query_result_multiple_results_json,
    query_result_no_result_json,
    query_result_single_result_json
)


def test_determine_original_item_single_item():
    # Arrange
    mediahaven_result = json.loads(query_result_single_result_json)
    # Act
    fragment_id = determine_original_item(mediahaven_result) 
    # Assert
    assert fragment_id == "123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525"

def test_determine_original_item_multiple_items_2():
    # Arrange
    mediahaven_result = json.loads(query_result_multiple_results_json)
    # Act
    fragment_id = determine_original_item(mediahaven_result) 
    # Assert
    assert fragment_id == "1234567891011121314151617181920212223242526272829303132333435363dfe24b95373a4ca6b00ebfee3447bd75"

def test_determine_original_item_multiple_items_3():
    # Arrange
    mediahaven_result = json.loads(query_result_multiple_results_json_3)
    # Act
    fragment_id = determine_original_item(mediahaven_result) 
    # Assert
    assert fragment_id == "911590738667861623378452998032598893744975670506425831782315371606163411184739903652215505881300"

