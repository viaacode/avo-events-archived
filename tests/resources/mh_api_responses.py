#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

folder = os.path.join(os.getcwd(), "tests", "resources", "mh_api_responses")


def _load_resource(filename):
    with open(os.path.join(folder, filename), "rb") as f:
        contents = f.read()
    return contents


fragment_info = _load_resource("fragment_info.json")
query_result_multiple_results = _load_resource("query_result_multiple_results.xml")
query_result_no_result = _load_resource("query_result_no_result.xml")
query_result_single_result = _load_resource("query_result_single_result.xml")
