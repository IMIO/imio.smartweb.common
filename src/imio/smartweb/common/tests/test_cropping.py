# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.cropping import SmartwebCroppingImageScalingFactory
from imio.smartweb.common.interfaces import ICropping
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.imagecropping.events import CroppingInfoChangedEvent
from plone.app.imagecropping.events import CroppingInfoRemovedEvent
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobImage
from plone.testing.z2 import Browser
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.event import notify

import os
import time
import transaction
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

    def test_cropping_factory(self):
        test_image = os.path.join(
            os.path.dirname(__file__), "resources/image_1800x700.png"
        )
        with open(test_image, "rb") as fd:
            self.folder.image = NamedBlobImage(data=fd.read(), filename=test_image)

        view = self.folder.restrictedTraverse("@@crop-image")
        view._crop(fieldname="image", scale="portrait_affiche", box=(1, 1, 200, 200))

        factory = SmartwebCroppingImageScalingFactory(self.folder)

        factory("image", "scale", 430, 608, "portrait_vignette")
        # same box as "affiche" scale
        self.assertEqual(factory.box, (1, 1, 200, 200))

        factory("image", "scale", 100, 100, "preview")
        # uncropped scale
        self.assertIsNone(factory.box)

        factory("image", "scale", 100, 100)
        self.assertIsNone(factory.box)

        api.content.transition(self.folder, "publish")
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.open(f"{self.folder.absolute_url()}/@@images/image/portrait_liste")
        self.assertEqual("image/png", browser.headers["content-type"])
        # only one crop is saved (the big one)
        annotation = IAnnotations(self.folder).get(PAI_STORAGE_KEY)
        self.assertEqual(annotation, {"image_portrait_affiche": (1, 1, 200, 200)})

    def test_cropping_view(self):
        cropping_view = getMultiAdapter(
            (self.folder, self.request), name="croppingeditor"
        )
        self.assertEqual(len(list(cropping_view._scales("image"))), 14)
        size = [100, 100]
        scale_info = cropping_view._scale_info("image", "scale", size, size)
        self.assertEqual(scale_info["title"], "Scale")
        scale_info = cropping_view._scale_info("image", "portrait_scale", size, size)
        self.assertEqual(scale_info["title"], "Portrait")
        scale_info = cropping_view._scale_info("image", "paysage_scale", size, size)
        self.assertEqual(scale_info["title"], "Paysage")
        scale_info = cropping_view._scale_info("image", "carre_scale", size, size)
        self.assertEqual(scale_info["title"], "Carre")
        scale_info = cropping_view._scale_info("image", "unexpected_scale", size, size)
        self.assertEqual(scale_info["title"], "Unexpected_Scale")

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
