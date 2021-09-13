#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import urllib
from typing import Any, Callable, Dict

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException


class MediaObjectNotFoundException(Exception):
    """Exception raised when MediaHaven doesn't find a media object given the ID."""


class AuthenticationException(Exception):
    """Exception raised when authentication fails."""


class MediahavenService:
    def __init__(self, config: dict):
        self.cfg: Dict[str, Any] = config
        self.token_info: Dict = {}
        self.url = f"{self.cfg['mediahaven']['host']}/media/"

    def __authenticate(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper_authenticate(self, *args, **kwargs):
            if not self.token_info:
                self.token_info = self.__get_token()
            try:
                return function(self, *args, **kwargs)
            except AuthenticationException:
                self.token_info = self.__get_token()
            return function(self, *args, **kwargs)

        return wrapper_authenticate

    def __get_token(self) -> dict:
        """Gets an OAuth token that can be used in mediahaven requests to authenticate."""
        user: str = self.cfg["mediahaven"]["username"]
        password: str = self.cfg["mediahaven"]["password"]
        url: str = self.cfg["mediahaven"]["host"] + "/oauth/access_token"
        payload = {"grant_type": "password"}

        try:
            r = requests.post(
                url,
                auth=HTTPBasicAuth(user.encode("utf-8"), password.encode("utf-8")),
                data=payload,
            )

            if r.status_code != 201:
                raise RequestException(
                    f"Failed to get a token. Status: {r.status_code}"
                )
            token_info = r.json()
        except RequestException as e:
            raise e
        return token_info

    @__authenticate
    def query(self, query_key_values) -> bytes:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.token_info['access_token']}",
            "Accept": "application/vnd.mediahaven.v2+json",
        }

        # Construct URL query parameters as "+(k1:v1) +(k2:v2) +(k3:v3) ..."
        query = " ".join([f'+({":".join(map(str, k_v))})' for k_v in query_key_values])

        params_dict: Dict[str, str] = {
            "q": query,
            "nrOfResults": 1000,
        }
        # Encode the spaces in the query parameters as %20 and not +
        params = urllib.parse.urlencode(params_dict, quote_via=urllib.parse.quote)

        # Send the GET request
        response = requests.get(
            self.url,
            headers=headers,
            params=params,
        )

        if response.status_code == 401:
            # AuthenticationException triggers a retry with a new token
            raise AuthenticationException(response.text)

        # If there is an HTTP error, raise it
        response.raise_for_status()

        return response.json()

    @__authenticate
    def get_fragment(self, fragment_id: str, content_type: str = "json") -> dict:
        url: str = f"{self.cfg['mediahaven']['host']}/media/{fragment_id}"

        headers: dict = {
            "Authorization": f"Bearer {self.token_info['access_token']}",
            "Accept": f"application/vnd.mediahaven.v2+{content_type}",
        }

        response = requests.get(
            url,
            headers=headers,
        )

        if response.status_code == 401:
            # AuthenticationException triggers a retry with a new token
            raise AuthenticationException(response.text)

        if response.status_code in (400, 404):
            raise MediaObjectNotFoundException(response.json())

        if content_type == "json":
            return response.json()
        else:
            return response.content

    @__authenticate
    def update_metadata(self, fragment_id: str, sidecar: bytes) -> bool:
        url: str = f"{self.cfg['mediahaven']['host']}/media/{fragment_id}"

        headers: dict = {
            "Authorization": f"Bearer {self.token_info['access_token']}",
            "Accept": "application/vnd.mediahaven.v2+json",
        }

        data: dict = {"metadata": sidecar, "reason": "Add original metadata."}

        # Send the POST request, as multipart/form-data
        response = requests.post(url, headers=headers, files=data)

        if response.status_code == 401:
            # AuthenticationException triggers a retry with a new token
            raise AuthenticationException(response.text)

        # If there is an HTTP error, raise it
        response.raise_for_status()

        # Mediahaven returns 204 if successful
        return response.status_code == 204
