# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.textfield.value import RichTextValue
from zope.lifecycleevent import modified

import unittest


class TestText(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="My Root Folder",
        )

    def test_cleaning_text(self):
        document = api.content.create(
            container=self.folder,
            type="Document",
            title="My Doc",
        )
        text = RichTextValue("<p>Kam\x02oulox</p>", "text/html", "text/html")
        document.text = text
        modified(document)
        self.assertEqual(document.text.raw, "<p>Kamoulox</p>")
        self.assertEqual(document.text.mimeType, "text/html")
        self.assertEqual(document.text.outputMimeType, "text/html")

        document = api.content.create(
            container=self.folder,
            type="Document",
            title="My Doc",
            text=RichTextValue("<p>Kam\x02oulox</p>", "text/html", "text/html"),
        )
        self.assertEqual(document.text.raw, "<p>Kamoulox</p>")
