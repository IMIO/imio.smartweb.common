# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase
from imio.smartweb.common.viewlets.colophon import ColophonViewlet
from imio.smartweb.common.viewlets.skip_to_content import SkipToContentViewlet
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TestViewlets(ImioSmartwebCommonTestCase):
    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            id="folder",
        )

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

    def test_skip_to_content(self):
        logout()
        url = self.folder.absolute_url() + "/some_view"
        self.request["ACTUAL_URL"] = url
        self.request["QUERY_STRING"] = "foo=bar"
        viewlet = SkipToContentViewlet(self.folder, self.request, None)
        viewlet.update()
        html = viewlet.render()
        self.assertIn(
            'href="http://nohost/plone/folder/some_view?foo=bar#content"', html
        )
