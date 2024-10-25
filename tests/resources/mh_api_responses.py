#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

folder = os.path.join(os.getcwd(), "tests", "resources", "mh_api_responses")


def _load_resource(filename):
    with open(os.path.join(folder, filename), "rb") as f:
        contents = f.read()
    return contents


fragment_info_json = _load_resource("fragment_info.json")
fragment_info_xml = _load_resource("fragment_info.xml")
query_result_multiple_results_json_record_types = _load_resource("query_result_multiple_results_record_types.json")
query_result_multiple_results_json_3 = _load_resource("query_result_multiple_results_3.json")
query_result_multiple_results_json = _load_resource("query_result_multiple_results.json")
query_result_multiple_results_xml = _load_resource("query_result_multiple_results.xml")
query_result_no_result_json = _load_resource("query_result_no_result.json")
query_result_no_result_xml = _load_resource("query_result_no_result.xml")
query_result_single_result_json = _load_resource("query_result_single_result.json")
query_result_single_result_xml = _load_resource("query_result_single_result.xml")
