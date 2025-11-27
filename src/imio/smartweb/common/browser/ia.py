from imio.smartweb.common.config import APPLICATION_ID
from imio.smartweb.common.config import PROJECT_ID
from zope.publisher.browser import BrowserView

import json
import os


class BaseIAView(BrowserView):
    """
    Base view providing common headers and configuration for IA-related features.
    This class is shared across multiple projects, including imio.smartweb.core.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._headers = None

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "x-imio-application": APPLICATION_ID,
                "x-imio-municipality": PROJECT_ID,
            }
        return self._headers

    @property
    def headers_json(self):
        return json.dumps(self.headers)
