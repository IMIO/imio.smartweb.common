# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestPermissions(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.catalog = self.portal.portal_catalog
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            container=self.portal, type="Folder", id="folder"
        )
        self.doc = api.content.create(container=self.folder, type="Document", id="doc")

    def assertResultsWithRole(self, role, results_nb):
        setRoles(self.portal, TEST_USER_ID, [role])
        brains = self.catalog.searchResults(id="doc")
        self.assertEqual(len(brains), results_nb)

    def test_search_results_expired(self):
        self.assertResultsWithRole("Member", 1)
        self.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.doc.reindexObject()
        self.assertResultsWithRole("Member", 0)
        self.assertResultsWithRole("Contributor", 0)
        self.assertResultsWithRole("Editor", 1)
        self.assertResultsWithRole("Reader", 1)
        self.assertResultsWithRole("Reviewer", 1)
        self.assertResultsWithRole("Manager", 1)
        self.assertResultsWithRole("Site Administrator", 1)
