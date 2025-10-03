# src/your.pkg/browser/process.py
from imio.smartweb.common.config import IPA_URL
from zope.publisher.browser import BrowserView

import json
import requests


class BaseIAView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }


class ProcessTextExpandView(BaseIAView):

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        body = self.request.get("BODY", b"") or self.request.stdin.read() or b""
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}
        current_html = data.get("html", "")
        payload = {
            "input": current_html,
            "expansion_target": 50,
        }
        url = f"{IPA_URL}/expand-text"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            return current_html
        data = response.json()
        if not data:
            return current_html

        new_html = data.get("result")
        return json.dumps({"html": new_html})


class ProcessTextShorterView(BaseIAView):

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        body = self.request.get("BODY", b"") or self.request.stdin.read() or b""
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}
        current_html = data.get("html", "")
        payload = {
            "input": current_html,
            "expansion_target": 50,
        }
        url = f"{IPA_URL}/reduce-text"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            return current_html
        data = response.json()
        if not data:
            return current_html

        new_html = data.get("result")
        return json.dumps({"html": new_html})


class ProcessTextImproveView(BaseIAView):

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        body = self.request.get("BODY", b"") or self.request.stdin.read() or b""
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}
        current_html = data.get("html", "")
        payload = {
            "input": current_html,
            "expansion_target": 50,
        }
        url = f"{IPA_URL}/improve-text"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            return current_html
        data = response.json()
        if not data:
            return current_html

        new_html = data.get("result")
        return json.dumps({"html": new_html})
