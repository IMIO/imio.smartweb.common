# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase
from imio.smartweb.common.viewlets.colophon import ColophonViewlet
from plone.app.testing import login
from plone.app.testing import logout


class TestViewlets(ImioSmartwebCommonTestCase):

    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]

    def test_colophon(self):
        logout()
        viewlet = ColophonViewlet(self.portal, self.request, None)
        viewlet.update()
        html = viewlet.render()
        self.assertIn("Agent connection", html)

        login(self.portal, "test")
        viewlet.update()
        html = viewlet.render()
        self.assertNotIn("Agent connection", html)
