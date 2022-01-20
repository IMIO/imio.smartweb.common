# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.privacy.utils import get_all_consent_reasons
from plone import api
from Products.Five import BrowserView

import json


class PrivacyView(BrowserView):
    """ """

    def allow_iframes(self):
        self.request.response.setHeader("Content-type", "application/json")
        portal_privacy = api.portal.get_tool("portal_privacy")
        return json.dumps(portal_privacy.processingIsAllowed("show_genetic_embed"))

    def accept_or_refuse_all(self):
        form = self.request.form
        came_from = form.get("came_from")
        if not came_from:
            came_from = api.portal.get_navigation_root(self.context).absolute_url()
        accept_all = True if "consent" in form else False
        privacy_tool = api.portal.get_tool("portal_privacy")
        for reason in get_all_consent_reasons(privacy_tool):
            if accept_all:
                privacy_tool.consentToProcessing(reason.__name__)
            else:
                privacy_tool.objectToProcessing(reason.__name__)
        self.request.response.redirect(came_from)
        return ""
