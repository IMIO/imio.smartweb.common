# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import IAddress
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from imio.smartweb.common.utils import geocode_object
from imio.smartweb.common.utils import get_term_from_vocabulary
from imio.smartweb.common.utils import translate_vocabulary_term
from plone.formwidget.geolocation.geolocation import Geolocation
from unittest import mock
from zope.interface import implementer

import geopy
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
