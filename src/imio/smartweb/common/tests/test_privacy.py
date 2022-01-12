# -*- coding: utf-8 -*-

from email.utils import formatdate
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.z2 import Browser
from plone.transformchain.interfaces import ITransform
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter

import time
import unittest


class TestPrivacy(unittest.TestCase):

    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_iframe_transform(self):
        self.request.response["content-type"] = "text/html"
        privacy_handler = getMultiAdapter(
            (True, self.request), ITransform, name="imio.smartweb.common.privacy"
        )
        result = privacy_handler.transformUnicode(
            '<iframe src="http://host.com">', "utf-8"
        )
        self.assertIn('src=""', result)
        self.assertIn('gdpr-src="http://host.com"', result)
        self.assertIn('class="gdpr-iframe"', result)

        html = '<iframe src="http://host.com" width="2" height="4">'
        result = privacy_handler.transformUnicode(html, "utf-8")
        self.assertIn('width="0"', result)
        self.assertIn('height="0"', result)
        self.assertIn('gdpr-width="2"', result)
        self.assertIn('gdpr-height="4"', result)
        self.assertIn("This feature requires cookies acceptation", result)

        self.assertEqual(privacy_handler.transformBytes(html, "utf-8"), result)
        self.assertEqual(privacy_handler.transformIterable([html], "utf-8"), [result])

    def test_views(self):
        view = queryMultiAdapter((self.portal, self.request), name="allow_iframes")
        self.assertEqual(view(), "false")
        expiration_seconds = time.time() + (60 * 60 * 24 * 365)
        expires = formatdate(expiration_seconds, usegmt=True)
        self.request.response.setCookie(
            "dataprotection", "show_genetic_embed|1", path="/", expires=expires
        )
        self.assertEqual(view(), "true")

    def test_form(self):
        browser = Browser(self.layer["app"])
        browser.open("{}/@@consent".format(self.portal.absolute_url()))
        content = browser.contents
        self.assertIn(
            "Choose to opt in or out of various pieces of functionality.", content
        )
