# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from transaction import commit

import json
import unittest


class TestTaxonomy(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        commit()
        self.page = api.content.create(
            container=self.portal,
            type="Document",
            title="Test page",
        )

    def test_removing_unused_taxonomy_term(self):
        body_data = {
            "languages": ["fr", "en", "nl", "ru", "da", "de"],
            "tree": {
                "key": "0",
                "title": "Test vocabulary",
                "subnodes": [
                    {
                        "key": "1",
                        "translations": {
                            "da": "Informationsvidenskab",
                            "de": "Informatik",
                            "en": "Information Science",
                            "ru": "Информатику",
                        },
                        "subnodes": [
                            {
                                "key": "3",
                                "translations": {"da": "Kronologi", "en": "Chronology"},
                                "subnodes": [],
                            }
                        ],
                    }
                ],
                "default_language": "da",
            },
            "taxonomy": "collective.taxonomy.test",
        }
        json_str = json.dumps(body_data)
        bytes_data = json_str.encode("utf-8")
        self.request.set("BODY", bytes_data)
        self.request.method = "POST"
        result = self.portal.restrictedTraverse("@@taxonomy-import")()
        self.assertEqual(
            result,
            '{"status": "info", "message": "Your taxonomy has been saved with success."}',
        )
