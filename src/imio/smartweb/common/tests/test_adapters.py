# -*- coding: utf-8 -*-

from imio.smartweb.common.adapters import ImageContenttypeValidator
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone.namedfile.field import InvalidImageFile
from plone.namedfile.field import NamedBlobImage as NamedBlobImageField
from plone.namedfile.file import NamedBlobImage

import os
import unittest


class TestImageContenttypeValidator(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.field = NamedBlobImageField()
        self.field.__name__ = "image"

    def _load_image(self, filename):
        path = os.path.join(os.path.dirname(__file__), "resources", filename)
        with open(path, "rb") as fd:
            return NamedBlobImage(data=fd.read(), filename=filename)

    def test_validate_image_none(self):
        validator = ImageContenttypeValidator(self.field, None)
        self.assertFalse(validator())

    def test_validate_image_valid_mimetype(self):
        value = self._load_image("image.png")
        self.assertEqual(value.contentType, "image/png")
        validator = ImageContenttypeValidator(self.field, value)
        self.assertTrue(validator())

    def test_validate_image_invalid_mimetype(self):
        value = self._load_image("image.png")
        value.contentType = "application/pdf"
        validator = ImageContenttypeValidator(self.field, value)
        with self.assertRaises(InvalidImageFile):
            validator()
