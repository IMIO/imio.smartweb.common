from imio.smartweb.common.config import IPA_URL
from imio.smartweb.common.config import APPLICATION_ID
from imio.smartweb.common.config import PROJECT_ID
from Products.Five import BrowserView
from zope.publisher.browser import BrowserView

import json
import requests


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


class ProcessSuggestedTitlesView(BaseIAView):

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        current_html = self.request.form.get("text", "")
        payload = {
            "input": current_html,
            "expansion_target": 50,
        }
        url = f"{IPA_URL}/suggest-titles"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            return current_html
        data = response.json()
        if not data:
            return current_html
        return json.dumps(data)
