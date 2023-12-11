# -*- coding: utf-8 -*-

from DateTime import DateTime
from freezegun import freeze_time
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage

import unittest


class TestDescription(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    @freeze_time("2023-12-14 9:00:00")
    def test_added_content_image(self):
        # content types for which effective date is equal to created date (thank to subrscriber)
        content_types = ["File", "Image"]
        frozen_time = DateTime()

        for ct in content_types:
            obj = api.content.create(
                container=self.portal,
                type=ct,
                title=f"My {ct}",
            )
            if IFile.providedBy(obj):
                obj.file = NamedBlobFile(data="file data", filename="file.txt")

            elif IImage.providedBy(obj):
                obj.image = NamedBlobImage(data="file data", filename="file.txt")

            self.assertEqual(obj.effective(), frozen_time)
            # subscriber added_content fix effective as created date for Image content type
            self.assertEqual(obj.effective(), obj.created())
