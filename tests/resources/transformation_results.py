#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

folder = os.path.join(os.getcwd(), "tests", "resources", "transformation_results")


def _load_resource(filename):
    with open(os.path.join(folder, filename), "rb") as f:
        contents = f.read()
    return contents


sidecar = _load_resource("sidecar.xml")
