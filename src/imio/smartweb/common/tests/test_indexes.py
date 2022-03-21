# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import os
import unittest


class TestIndexes(unittest.TestCase):

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

    def test_subjects_in_searchable_text(self):
        catalog = api.portal.get_tool("portal_catalog")
        uuid = IUUID(self.folder)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertNotIn("foo", indexes.get("SearchableText"))
        self.folder.setSubject(["foo"])
        self.folder.reindexObject(idxs=["SearchableText"])
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertIn("foo", indexes.get("SearchableText"))

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
        self.assertEqual(indexes.get("breadcrumb"), "My Root Folder » My Sub Folder")

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
            "My Root Folder » My Sub Folder » My Sub Sub Folder",
        )

        folder.title = "My New Sub Folder"
        modified(folder, Attributes(IBasic, "IBasic.title"))
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"),
            "My Root Folder » My New Sub Folder » My Sub Sub Folder",
        )

        self.folder.title = "My New Root Folder"
        modified(self.folder, Attributes(IBasic, "IBasic.title"))
        api.content.move(sub_folder, self.folder)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"), "My New Root Folder » My Sub Sub Folder"
        )

    def test_has_leadimage(self):
        catalog = api.portal.get_tool("portal_catalog")
        uuid = IUUID(self.folder)
        self.assertEqual(len(api.content.find(has_leadimage=True)), 0)
        brain = api.content.find(UID=uuid)[0]
        self.assertEqual(brain.has_leadimage, False)
        test_image = os.path.join(os.path.dirname(__file__), "resources/image.png")
        with open(test_image, "rb") as fd:
            self.folder.image = NamedBlobImage(data=fd.read(), filename=test_image)
        self.folder.reindexObject()
        self.assertEqual(len(api.content.find(has_leadimage=True)), 1)
        brain = api.content.find(UID=uuid)[0]
        self.assertEqual(brain.has_leadimage, True)

        collection = api.content.create(
            container=self.portal,
            type="Collection",
            title="My Collection without lead image behavior",
        )
        collection.reindexObject()
        brain = api.content.find(UID=collection.UID())[0]
        self.assertEqual(brain.has_leadimage, False)
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("has_leadimage"), False)
        self.assertEqual(len(api.content.find(has_leadimage=True)), 1)

        image = api.content.create(
            container=self.portal,
            type="Image",
            title="My image",
        )
        with open(test_image, "rb") as fd:
            image.image = NamedBlobImage(data=fd.read(), filename=test_image)
        image.reindexObject()
        brain = api.content.find(UID=image.UID())[0]
        self.assertEqual(brain.has_leadimage, True)
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("has_leadimage"), True)
        self.assertEqual(len(api.content.find(has_leadimage=True)), 2)
