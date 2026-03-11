# -*- coding: utf-8 -*-

from imio.smartweb.common.ia.browser.views import BaseIAView
from imio.smartweb.common.ia.browser.views import ProcessSuggestedTitlesView
from imio.smartweb.common.browser.tiny.process import ProcessTextExpandView
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest.mock import MagicMock
from unittest.mock import patch

import requests
import unittest


class TestBaseIAViewHeaders(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def _make_view(self):
        view = BaseIAView(self.portal, self.request)
        view._headers = None
        return view

    @patch(
        "imio.smartweb.common.ia.browser.views.get_auth_token",
        return_value="mytoken",
    )
    def test_headers_include_authorization_when_token_is_string(self, mock_token):
        view = self._make_view()
        headers = view.headers
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer mytoken")

    @patch(
        "imio.smartweb.common.ia.browser.views.get_auth_token",
        return_value=MagicMock(spec=requests.Response),
    )
    def test_headers_no_authorization_when_token_is_response_object(self, mock_token):
        view = self._make_view()
        headers = view.headers
        self.assertNotIn("Authorization", headers)

    @patch(
        "imio.smartweb.common.ia.browser.views.get_auth_token",
        return_value="",
    )
    def test_headers_no_authorization_when_token_is_empty_string(self, mock_token):
        view = self._make_view()
        headers = view.headers
        self.assertNotIn("Authorization", headers)

    @patch(
        "imio.smartweb.common.ia.browser.views.get_auth_token",
        return_value="mytoken",
    )
    def test_headers_contain_required_fields(self, mock_token):
        view = self._make_view()
        headers = view.headers
        self.assertIn("accept", headers)
        self.assertIn("Content-Type", headers)
        self.assertIn("x-imio-application", headers)
        self.assertIn("x-imio-municipality", headers)


class TestProcessSuggestedTitlesViewHeaders(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    @patch("imio.smartweb.common.ia.browser.views.requests.post")
    @patch(
        "imio.smartweb.common.ia.browser.views.get_auth_token",
        return_value="mytoken",
    )
    def test_suggest_titles_passes_authorization_header(
        self, mock_token, mock_post
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["Title A", "Title B"]
        mock_post.return_value = mock_response

        self.request.form["text"] = "Some HTML content"
        view = ProcessSuggestedTitlesView(self.portal, self.request)
        view._headers = None
        view()

        _, kwargs = mock_post.call_args
        sent_headers = kwargs.get("headers", mock_post.call_args[0][1] if len(mock_post.call_args[0]) > 1 else {})
        self.assertIn("Authorization", sent_headers)
        self.assertEqual(sent_headers["Authorization"], "Bearer mytoken")


class TestProcessTextExpandViewHeaders(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    @patch("imio.smartweb.common.browser.tiny.process.requests.post")
    @patch(
        "imio.smartweb.common.ia.browser.views.get_auth_token",
        return_value="mytoken",
    )
    def test_expand_text_passes_authorization_header(self, mock_token, mock_post):
        import json as _json

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "<p>expanded</p>"}
        mock_post.return_value = mock_response

        body = _json.dumps({"html": "<p>hello</p>"}).encode("utf-8")
        self.request["BODY"] = body
        view = ProcessTextExpandView(self.portal, self.request)
        view._headers = None
        view()

        _, kwargs = mock_post.call_args
        sent_headers = kwargs.get("headers", {})
        self.assertIn("Authorization", sent_headers)
        self.assertEqual(sent_headers["Authorization"], "Bearer mytoken")
