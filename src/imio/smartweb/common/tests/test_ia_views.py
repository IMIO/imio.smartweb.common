# -*- coding: utf-8 -*-

from imio.omnia.core.interfaces import IOmniaCoreAPIService
from imio.smartweb.common.ia.browser.views import BaseIAView
from imio.smartweb.common.ia.browser.views import BaseProcessCategorizeContentView
from imio.smartweb.common.ia.browser.views import ProcessSuggestedTitlesView
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import unittest


VIEWS = "imio.smartweb.common.ia.browser.views"


class ConcreteCategorizeView(BaseProcessCategorizeContentView):
    """Concrete implementation of the abstract categorize base view."""

    def _get_all_text(self):
        return "some text"

    def _process_specific(self, all_text="", results={}):
        results["specific"] = all_text


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

    @patch("imio.smartweb.common.ia.browser.views.getMultiAdapter")
    def test_suggest_titles_returns_input_when_no_data(self, mock_get_adapter):
        service = MagicMock()
        service.suggest_titles.return_value = []  # falsy -> return the input html
        mock_get_adapter.return_value = service

        self.request.form["text"] = "kept html"
        view = ProcessSuggestedTitlesView(self.portal, self.request)
        self.assertEqual(view(), "kept html")


class TestBaseProcessCategorizeContentView(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def _make_view(self, context=None):
        return ConcreteCategorizeView(context or SimpleNamespace(), self.request)

    def test_abstract_methods_raise(self):
        view = BaseProcessCategorizeContentView(SimpleNamespace(), self.request)
        with self.assertRaises(NotImplementedError):
            view._get_all_text()
        with self.assertRaises(NotImplementedError):
            view._process_specific()

    def test_ask_categorization_returns_empty_on_error(self):
        view = self._make_view()
        service = MagicMock()
        service.categorize_content.side_effect = Exception("boom")
        with patch.object(BaseProcessCategorizeContentView, "ia_service", service):
            self.assertEqual(view._ask_categorization_to_ia("text", []), {})

    def test_merge_existing_tokens(self):
        view = self._make_view()
        full_voc = [
            {"token": "a", "title": "A"},
            {"token": "b", "title": "B"},
        ]
        # append: existing "b" is missing from the IA response -> added back
        merged = view._merge_existing_tokens([{"token": "a"}], ["b"], full_voc)
        self.assertEqual({t["token"] for t in merged}, {"a", "b"})
        # dedup: existing "a" already present -> not duplicated
        merged = view._merge_existing_tokens([{"token": "a"}], ["a"], full_voc)
        self.assertEqual(len(merged), 1)
        # unknown token: not found in the vocabulary -> skipped
        self.assertEqual(view._merge_existing_tokens([], ["zzz"], full_voc), [])
        # empty / None existing tokens -> list unchanged
        self.assertEqual(
            view._merge_existing_tokens([{"token": "a"}], [], full_voc),
            [{"token": "a"}],
        )
        self.assertEqual(
            view._merge_existing_tokens([{"token": "a"}], None, full_voc),
            [{"token": "a"}],
        )

    @patch(f"{VIEWS}.get_vocabulary")
    @patch(f"{VIEWS}.getMultiAdapter")
    def test_call_builds_categorization(self, mock_get_adapter, mock_get_voc):
        # Vocabulary terms (same for IAm and Topics for simplicity)
        mock_get_voc.return_value = [
            SimpleNamespace(title="Culture", token="culture"),
            SimpleNamespace(title="Sport", token="sport"),
        ]
        service = MagicMock()
        service.categorize_content.return_value = {
            "result": [{"title": "Sport", "token": "sport"}]
        }
        mock_get_adapter.return_value = service

        context = SimpleNamespace(iam=["culture"], topics=[])
        view = self._make_view(context)
        result = json.loads(view())

        self.assertTrue(result["ok"])
        data = result["data"]
        # IAm: IA returned "sport"; existing "culture" merged back in
        self.assertEqual(
            {t["token"] for t in data["form-widgets-IAm-iam"]}, {"sport", "culture"}
        )
        # Topics: no existing tokens -> only the IA result
        self.assertEqual(
            {t["token"] for t in data["form-widgets-ITopics-topics"]}, {"sport"}
        )
        # _process_specific hook ran
        self.assertEqual(data["specific"], "some text")

    @patch(f"{VIEWS}.get_vocabulary")
    @patch(f"{VIEWS}.getMultiAdapter")
    def test_call_skips_when_no_ia_data(self, mock_get_adapter, mock_get_voc):
        mock_get_voc.return_value = [SimpleNamespace(title="Sport", token="sport")]
        service = MagicMock()
        service.categorize_content.return_value = None  # falsy -> processes skip
        mock_get_adapter.return_value = service

        view = self._make_view(SimpleNamespace(iam=[], topics=[]))
        result = json.loads(view())

        self.assertTrue(result["ok"])
        self.assertNotIn("form-widgets-IAm-iam", result["data"])
        self.assertNotIn("form-widgets-ITopics-topics", result["data"])
        self.assertEqual(result["data"]["specific"], "some text")
