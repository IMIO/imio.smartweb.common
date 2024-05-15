# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import IAddress
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from imio.smartweb.common.utils import clean_invisible_char
from imio.smartweb.common.utils import geocode_object
from imio.smartweb.common.utils import get_term_from_vocabulary
from imio.smartweb.common.utils import get_uncroppable_scales_infos
from imio.smartweb.common.utils import remove_cropping
from imio.smartweb.common.utils import show_warning_for_scales
from imio.smartweb.common.utils import translate_vocabulary_term
from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobImage
from Products.statusmessages.interfaces import IStatusMessage
from unittest import mock
from unittest.mock import patch
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer

import geopy
import os
import unittest


@implementer(IAddress)
class GeolocatedObject(object):
    """Dummy class for geolocation tests"""

    street = None
    number = None
    complement = None
    zipcode = None
    city = None
    country = None

    def reindexObject(self, idxs):
        return


class TestUtils(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_get_term_from_vocabulary(self):
        term = get_term_from_vocabulary("imio.smartweb.vocabulary.Topics", "culture")
        self.assertEqual(term.title, "Culture")

        term = get_term_from_vocabulary("imio.smartweb.vocabulary.IAm", "parent")
        self.assertEqual(term.title, "Parent")

        term = get_term_from_vocabulary("imio.smartweb.vocabulary.IAm", "non_existing")
        self.assertEqual(term.title, "non_existing")

    def test_translate_vocabulary_term(self):
        self.assertEqual(
            translate_vocabulary_term("imio.smartweb.vocabulary.Countries", None),
            "",
        )
        self.assertEqual(
            translate_vocabulary_term("imio.smartweb.vocabulary.Countries", "be"),
            "Belgium",
        )
        self.assertEqual(
            translate_vocabulary_term("imio.smartweb.vocabulary.Countries", "be", "fr"),
            "Belgique",
        )
        self.assertEqual(
            translate_vocabulary_term("imio.smartweb.vocabulary.Countries", "be", "nl"),
            "België",
        )
        with patch("plone.api.portal.get_current_language", return_value="fr"):
            self.assertEqual(
                translate_vocabulary_term("imio.smartweb.vocabulary.Countries", "be"),
                "Belgique",
            )

    def test_geolocation(self):
        attr = {"geocode.return_value": mock.Mock(latitude=1, longitude=2)}
        geopy.geocoders.Nominatim = mock.Mock(return_value=mock.Mock(**attr))

        obj = GeolocatedObject()
        obj.geolocation = Geolocation(0, 0)

        geocoded = geocode_object(obj)
        self.assertFalse(geocoded)
        self.assertEqual(obj.geolocation.latitude, 0)
        self.assertEqual(obj.geolocation.longitude, 0)

        obj.street = "My beautiful street"
        geocoded = geocode_object(obj)
        self.assertTrue(geocoded)
        self.assertEqual(obj.geolocation.latitude, 1)
        self.assertEqual(obj.geolocation.longitude, 2)

    def test_get_uncroppable_scales_infos(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            id="folder",
        )
        show_warning_for_scales(folder, self.request)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 0)

        test_image = os.path.join(
            os.path.dirname(__file__), "resources/image_1800x700.png"
        )
        with open(test_image, "rb") as fd:
            folder.image = NamedBlobImage(data=fd.read(), filename=test_image)

        sizes = {"size1": (1000, 500), "size2": (65536, 500)}
        scales = []
        result = get_uncroppable_scales_infos(folder.image, sizes, scales)
        self.assertEqual(result, {})

        sizes = {"size1": (1000, 500), "size2": (65536, 500)}
        scales = ["size1", "size2"]
        result = get_uncroppable_scales_infos(folder.image, sizes, scales)
        self.assertEqual(result, {})

        sizes = {"size1": (1900, 500), "size2": (65536, 500)}
        scales = ["size1", "size2"]
        result = get_uncroppable_scales_infos(folder.image, sizes, scales)
        self.assertEqual(len(result["scales"]), 1)
        self.assertEqual(result["min_width"], "1900")
        self.assertEqual(result["min_height"], "500")
        self.assertEqual(result["width"], "1800")
        self.assertEqual(result["height"], "700")

        sizes = {"size1": (1900, 400), "size2": (1700, 600), "size3": (65536, 800)}
        scales = ["size1", "size2", "size3"]
        result = get_uncroppable_scales_infos(folder.image, sizes, scales)
        self.assertEqual(len(result["scales"]), 2)
        self.assertEqual(result["min_width"], "1900")
        self.assertEqual(result["min_height"], "800")

    def test_show_warning_for_scales(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            id="folder",
        )
        show_warning_for_scales(folder, self.request)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 0)

        test_image = os.path.join(os.path.dirname(__file__), "resources/image.png")
        with open(test_image, "rb") as fd:
            folder.image = NamedBlobImage(data=fd.read(), filename=test_image)
        show_warning_for_scales(folder, self.request)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 1)
        self.assertEqual(
            show[0].message,
            'The image uploaded in the "Lead Image" field may be degraded because '
            "it does not meet the required minimum dimensions of 1320px width by 768px height "
            "(uploaded image size: 215px width by 56px height). "
            "You can see the detail via the Cropping menu.",
        )

        test_image = os.path.join(
            os.path.dirname(__file__), "resources/image_1800x700.png"
        )
        with open(test_image, "rb") as fd:
            folder.image = NamedBlobImage(data=fd.read(), filename=test_image)
        show_warning_for_scales(folder, self.request)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 1)
        self.assertEqual(
            show[0].message,
            'The image uploaded in the "Lead Image" field may be degraded because '
            "it does not meet the required minimum dimensions of 1320px width by 768px height "
            "(uploaded image size: 1800px width by 700px height). "
            "You can see the detail via the Cropping menu.",
        )

        test_image = os.path.join(
            os.path.dirname(__file__), "resources/image_1400x800.png"
        )
        with open(test_image, "rb") as fd:
            folder.image = NamedBlobImage(data=fd.read(), filename=test_image)
        show_warning_for_scales(folder, self.request)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 0)

        test_image = os.path.join(os.path.dirname(__file__), "resources/image.png")
        with open(test_image, "rb") as fd:
            folder.image = NamedBlobImage(data=fd.read(), filename=test_image)
        logout()
        show_warning_for_scales(folder, self.request)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 0)

    def test_remove_cropping(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
            id="folder",
        )
        test_image = os.path.join(os.path.dirname(__file__), "resources/image.png")
        with open(test_image, "rb") as fd:
            folder.image = NamedBlobImage(data=fd.read(), filename=test_image)
        view = folder.restrictedTraverse("@@crop-image")
        view._crop(fieldname="image", scale="portrait_affiche", box=(1, 1, 200, 200))
        annotation = IAnnotations(folder).get(PAI_STORAGE_KEY)
        self.assertEqual(annotation, {"image_portrait_affiche": (1, 1, 200, 200)})

        remove_cropping(folder, "image", ["portrait_affiche"])
        self.assertEqual(annotation, {})

    def test_clean_invisible_char(self):
        txt = "<p>Kam\x02oulox</p>"
        clean_txt = clean_invisible_char(txt)
        self.assertEqual(clean_txt, "<p>Kamoulox</p>")

        clean_txt = clean_invisible_char(None)
        self.assertIsNone(clean_txt)
