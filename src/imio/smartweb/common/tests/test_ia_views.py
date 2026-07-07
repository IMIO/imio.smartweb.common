# -*- coding: utf-8 -*-

from imio.omnia.core.interfaces import IOmniaCoreAPIService
from imio.smartweb.common.ia.browser.views import BaseIAView
from imio.smartweb.common.ia.browser.views import ProcessSuggestedTitlesView
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import unittest


class TestBaseIAViewService(unittest.TestCase):
    """The IA service (URL + authentication) is provided by imio.omnia.core
    through the IOmniaCoreAPIService adapter."""

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    @patch("imio.smartweb.common.ia.browser.views.getMultiAdapter")
    def test_ia_service_uses_omnia_adapter(self, mock_get_adapter):
        service = MagicMock()
        mock_get_adapter.return_value = service
        view = BaseIAView(self.portal, self.request)

        self.assertIs(view.ia_service, service)
        mock_get_adapter.assert_called_once_with(
            (self.portal, self.request), IOmniaCoreAPIService
        )


class TestProcessSuggestedTitlesView(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    @patch("imio.smartweb.common.ia.browser.views.getMultiAdapter")
    def test_suggest_titles_delegates_to_service(self, mock_get_adapter):
        service = MagicMock()
        service.suggest_titles.return_value = ["Title A", "Title B"]
        mock_get_adapter.return_value = service

        self.request.form["text"] = "Some HTML content"
        view = ProcessSuggestedTitlesView(self.portal, self.request)
        result = view()

        service.suggest_titles.assert_called_once_with("Some HTML content")
        self.assertEqual(json.loads(result), ["Title A", "Title B"])

    @patch("imio.smartweb.common.ia.browser.views.getMultiAdapter")
    def test_suggest_titles_returns_input_on_error(self, mock_get_adapter):
        service = MagicMock()
        service.suggest_titles.side_effect = Exception("boom")
        mock_get_adapter.return_value = service

        self.request.form["text"] = "fallback text"
        view = ProcessSuggestedTitlesView(self.portal, self.request)
        self.assertEqual(view(), "fallback text")
