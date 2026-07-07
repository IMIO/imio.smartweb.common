# -*- coding: utf-8 -*-

from collective.taxonomy.jsonimpl import EditTaxonomyData as baseEditTaxonomyData
from imio.smartweb.common.browser.collective_taxonomy_controlpanel import (
    DeleteTaxonomyData,
)
from imio.smartweb.common.browser.collective_taxonomy_controlpanel import (
    EditTaxonomyData,
)
from Products.Five import BrowserView
from unittest import mock

import json
import unittest

MODULE = "imio.smartweb.common.browser.collective_taxonomy_controlpanel"


class FakeRequest:
    """Minimal request exposing only the BODY lookup the view relies on."""

    def __init__(self, body):
        self._body = body

    def get(self, key, default=None):
        if key == "BODY":
            return self._body
        return default


def make_brain(term_ids, url="http://nohost/doc", title="My doc"):
    """A catalog brain carrying the taxonomy metadata column."""
    brain = mock.Mock()
    brain.taxonomy_contact_category = list(term_ids)
    obj = mock.Mock()
    obj.absolute_url.return_value = url
    obj.Title.return_value = title
    brain.getObject.return_value = obj
    return brain


class TestEditTaxonomyData(unittest.TestCase):
    def test_subclasses_browserview(self):
        # EditTaxonomyData adds no behaviour of its own; it only combines the
        # collective.taxonomy edit view with a Zope BrowserView.
        self.assertTrue(issubclass(EditTaxonomyData, baseEditTaxonomyData))
        self.assertTrue(issubclass(EditTaxonomyData, BrowserView))


class TestDeleteTaxonomyData(unittest.TestCase):
    def _run(self, body, brains):
        taxonomy = mock.Mock()
        taxonomy.getGeneratedName.return_value = (
            "collective.taxonomy.generated.contact_category"
        )
        taxonomy.getShortName.return_value = "contact_category"
        catalog = mock.Mock()
        catalog.searchResults.return_value = brains
        with mock.patch(f"{MODULE}.queryUtility", return_value=taxonomy), mock.patch(
            f"{MODULE}.api"
        ) as api_mock:
            api_mock.portal.get_tool.return_value = catalog
            request = FakeRequest(json.dumps(body).encode("utf-8"))
            view = DeleteTaxonomyData(mock.Mock(), request)
            return json.loads(view.check_delete_taxonomy())

    def test_term_in_use_returns_error(self):
        brains = [make_brain(["1"], url="http://nohost/doc")]
        result = self._run({"termId": "1"}, brains)
        self.assertEqual(result["status"], "error")
        self.assertIn("http://nohost/doc", result["message"])

    def test_unused_term_returns_success(self):
        brains = [make_brain(["1"])]
        result = self._run({"termId": "999"}, brains)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Suppression autorisée")

    def test_no_term_id_returns_success(self):
        # No termId -> empty set -> never intersects any brain.
        brains = [make_brain(["1"])]
        result = self._run({}, brains)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Suppression autorisée")

    def test_brain_without_taxonomy_metadata_is_skipped(self):
        # A brain lacking the metadata column must not raise and must not match.
        brain = mock.Mock(spec=[])  # spec=[] -> hasattr() is False
        result = self._run({"termId": "1"}, [brain])
        self.assertEqual(result["status"], "success")
