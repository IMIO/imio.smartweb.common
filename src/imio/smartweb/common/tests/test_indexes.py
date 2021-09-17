# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import unittest


class IndexesTest(unittest.TestCase):

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

    def test_breadcrumb(self):
        catalog = api.portal.get_tool("portal_catalog")
        folder = api.content.create(
            container=self.folder,
            type="Folder",
            title="My Sub Folder",
        )
        uuid = IUUID(folder)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("breadcrumb"), "My Root Folder > My Sub Folder")

        sub_folder = api.content.create(
            container=folder,
            type="Folder",
            title="My Sub Sub Folder",
        )
        uuid = IUUID(sub_folder)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"),
            "My Root Folder > My Sub Folder > My Sub Sub Folder",
        )

        folder.title = "My New Sub Folder"
        modified(folder, Attributes(IBasic, "IBasic.title"))
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"),
            "My Root Folder > My New Sub Folder > My Sub Sub Folder",
        )

        self.folder.title = "My New Root Folder"
        modified(self.folder, Attributes(IBasic, "IBasic.title"))
        api.content.move(sub_folder, self.folder)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"), "My New Root Folder > My Sub Sub Folder"
        )
