# -*- coding: utf-8 -*-

from plone import api
from Products.Five import BrowserView

import json


class PrivacyView(BrowserView):
    """ """

    def allow_iframes(self):
        self.request.response.setHeader("Content-type", "application/json")
        portal_privacy = api.portal.get_tool("portal_privacy")
        return json.dumps(portal_privacy.processingIsAllowed("show_genetic_embed"))
