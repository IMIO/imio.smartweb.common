# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import ICropping
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from plone import api
from plone.app.imagecropping.events import CroppingInfoChangedEvent
from plone.app.imagecropping.events import CroppingInfoRemovedEvent
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getMultiAdapter
from zope.event import notify

import time
import unittest


class TestCropping(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            id="folder",
        )

    def test_cropping_adapter(self):
        adapter = ICropping(self.folder, alternate=None)
        self.assertIsNotNone(adapter)
        self.assertNotIn("banner", adapter.get_scales("image", self.request))

        image = api.content.create(
            container=self.folder,
            type="Image",
            title="My image",
            id="my-image",
        )
        adapter = ICropping(image, alternate=None)
        self.assertIsNotNone(adapter)
        self.assertEqual([], adapter.get_scales("image", self.request))

    def test_cropping_view(self):
        cropping_view = getMultiAdapter(
            (self.folder, self.request), name="croppingeditor"
        )
        self.assertEqual(len(list(cropping_view._scales("image"))), 11)

    def test_modified_cropping(self):
        brain = api.content.find(UID=self.folder.UID())[0]
        dt_before = brain.ModificationDate
        time.sleep(1)
        notify(CroppingInfoChangedEvent(self.folder))
        brain = api.content.find(UID=self.folder.UID())[0]
        dt_after = brain.ModificationDate
        self.assertNotEqual(dt_before, dt_after)

        brain = api.content.find(UID=self.folder.UID())[0]
        dt_before = brain.ModificationDate
        time.sleep(1)
        notify(CroppingInfoRemovedEvent(self.folder))
        brain = api.content.find(UID=self.folder.UID())[0]
        dt_after = brain.ModificationDate
        self.assertNotEqual(dt_before, dt_after)
