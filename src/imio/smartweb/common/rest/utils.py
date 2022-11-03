# -*- coding: utf-8 -*-

from zope.globalrequest import getRequest


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
