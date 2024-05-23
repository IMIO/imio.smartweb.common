# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest.mock import patch
from zope.component import queryMultiAdapter

import json
import unittest


class TestVocabulary(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.document = api.content.create(
            container=self.portal,
            type="Document",
            title="My Doc",
        )

    def test_getvocabulary(self):
        self.request.form = {
            "name": "imio.smartweb.vocabulary.Topics",
            "field": "topics",
        }
        view = queryMultiAdapter((self.document, self.request), name="getVocabulary")
        result = json.loads(view())
        self.assertEqual(result["results"][0]["id"], "entertainment")
        self.assertEqual(result["results"][0]["text"], "Entertainment")
        with patch("plone.api.portal.get_current_language", return_value="fr"):
            view = queryMultiAdapter(
                (self.document, self.request), name="getVocabulary"
            )
            result = json.loads(view())
            self.assertEqual(result["results"][0]["id"], "entertainment")
            self.assertEqual(
                result["results"][0]["text"], "Activités et divertissement"
            )
