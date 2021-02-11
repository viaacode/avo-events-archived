#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)


@app.route("/health/live")
def liveness_check() -> str:
    """Can be used to check if the app is responsive.

    Returns:
        str: OK if the app is running.
    """
    return "OK"
