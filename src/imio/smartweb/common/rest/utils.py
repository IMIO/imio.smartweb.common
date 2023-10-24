# -*- coding: utf-8 -*-

from more_itertools import chunked
from zope.globalrequest import getRequest

import hashlib
import json
import logging
import requests

logger = logging.getLogger("imio.smartweb.core")


def get_restapi_query_lang(query=None):
    if query is None:
        request = getRequest()
        query = request.form
    langs = [
        key.split("translated_in_")[1]
        for key in query
        if key.startswith("translated_in_")
    ]
    if not langs or len(langs) > 1:
        # we don't know how to handle multiple languages query
        return "fr"
    return langs[0]


def batch_results(iterable, batch_size):
    return list(chunked(iterable, batch_size, strict=False))


def get_json(url, auth=None, timeout=5):
    headers = {"Accept": "application/json"}
    if auth is not None:
        headers["Authorization"] = auth
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout raised for requests : {url}")
        return None
    except Exception:
        return None
    if response.status_code != 200:
        return None
    return json.loads(response.text)


def hash_md5(text):
    return hashlib.md5(text.encode()).hexdigest()
