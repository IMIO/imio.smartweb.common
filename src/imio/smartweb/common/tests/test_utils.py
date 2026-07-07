# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import IAddress
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from imio.smartweb.common.utils import _get_pil_mimetype
from imio.smartweb.common.utils import activate_sending_data_to_odwb_for_staging
from imio.smartweb.common.utils import clean_invisible_char
from imio.smartweb.common.utils import geocode_object
from imio.smartweb.common.utils import get_entities_vocabulary
from imio.smartweb.common.utils import get_image_format
from imio.smartweb.common.utils import get_json
from imio.smartweb.common.utils import get_parent_of_type
from imio.smartweb.common.utils import get_parent_providing
from imio.smartweb.common.utils import get_term_from_vocabulary
from imio.smartweb.common.utils import get_uncroppable_scales_infos
from imio.smartweb.common.utils import get_vocabulary
from imio.smartweb.common.utils import is_log_active
from imio.smartweb.common.utils import is_staging_or_local
from imio.smartweb.common.utils import remove_cropping
from imio.smartweb.common.utils import rich_description
from imio.smartweb.common.utils import show_warning_for_scales
from imio.smartweb.common.utils import translate_vocabulary_term
from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IPloneSiteRoot
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobImage
from Products.statusmessages.interfaces import IStatusMessage
from types import SimpleNamespace
from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import patch
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.interface import Interface

import geopy
import os
import requests
import unittest


class IMarkerNobodyProvides(Interface):
    """Marker interface no object in the hierarchy provides."""


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text


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
        obj = GeolocatedObject()
        obj.geolocation = Geolocation(0, 0)

        geocoded = geocode_object(obj)
        self.assertFalse(geocoded)
        self.assertEqual(obj.geolocation.latitude, 0)
        self.assertEqual(obj.geolocation.longitude, 0)

        obj.street = "My beautiful street"
        with patch("imio.smartweb.common.utils._geocode") as mock_geocode:
            mock_geocode.return_value = mock.Mock(latitude=1, longitude=2)
            geocoded = geocode_object(obj)
        self.assertTrue(geocoded)
        self.assertEqual(obj.geolocation.latitude, 1)
        self.assertEqual(obj.geolocation.longitude, 2)

    def test_geocode_object_geocoder_unavailable(self):
        obj = GeolocatedObject()
        obj.street = "Test Street"
        obj.number = "1"
        obj.complement = ""
        obj.zipcode = "12345"
        obj.city = "Testville"
        obj.country = "be"
        with patch("imio.smartweb.common.utils._geocode") as mock_geocode:
            mock_geocode.side_effect = geopy.exc.GeocoderUnavailable
            result = geocode_object(obj)
            self.assertFalse(result)

    def test_geocode_object_geocoder_rate_limited(self):
        obj = GeolocatedObject()
        obj.street = "Test Street"
        obj.number = "1"
        obj.complement = ""
        obj.zipcode = "12345"
        obj.city = "Testville"
        obj.country = "be"
        with patch("imio.smartweb.common.utils._geocode") as mock_geocode:
            mock_geocode.side_effect = geopy.exc.GeocoderRateLimited("rate limited")
            result = geocode_object(obj)
            self.assertFalse(result)

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

    # ------------------------------
    # get_json
    # ------------------------------
    def test_get_json_success_with_auth(self):
        with patch(
            "imio.smartweb.common.utils.requests.get",
            return_value=FakeResponse(200, '{"a": 1}'),
        ) as mget:
            result = get_json("http://x", auth="Bearer TOKEN")
        self.assertEqual(result, {"a": 1})
        headers = mget.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer TOKEN")

    def test_get_json_timeout_returns_none(self):
        with patch(
            "imio.smartweb.common.utils.requests.get",
            side_effect=requests.exceptions.Timeout,
        ):
            self.assertIsNone(get_json("http://x"))

    def test_get_json_generic_error_returns_none(self):
        with patch(
            "imio.smartweb.common.utils.requests.get",
            side_effect=Exception("boom"),
        ):
            self.assertIsNone(get_json("http://x"))

    def test_get_json_non_200_returns_none(self):
        with patch(
            "imio.smartweb.common.utils.requests.get",
            return_value=FakeResponse(404, "not found"),
        ):
            self.assertIsNone(get_json("http://x"))

    def test_get_json_empty_body_returns_none(self):
        with patch(
            "imio.smartweb.common.utils.requests.get",
            return_value=FakeResponse(200, ""),
        ):
            self.assertIsNone(get_json("http://x"))

    # ------------------------------
    # get_vocabulary
    # ------------------------------
    def test_get_vocabulary(self):
        # obj is None -> falls back to the portal
        voc = get_vocabulary("imio.smartweb.vocabulary.Topics")
        self.assertEqual(len(voc), 17)
        # explicit obj branch
        voc = get_vocabulary("imio.smartweb.vocabulary.IAm", self.portal)
        self.assertEqual(len(voc), 10)

    # ------------------------------
    # get_entities_vocabulary
    # ------------------------------
    def test_get_entities_vocabulary_with_items(self):
        payload = {"items": [{"UID": "uid1", "title": "Entity 1"}]}
        with patch("imio.smartweb.common.utils.get_json", return_value=payload):
            voc = get_entities_vocabulary("imio.directory.Entity", "http://dir")
        self.assertEqual([t.value for t in voc], ["uid1"])
        self.assertEqual(voc.getTerm("uid1").title, "Entity 1")

    def test_get_entities_vocabulary_none_or_empty(self):
        with patch("imio.smartweb.common.utils.get_json", return_value=None):
            self.assertEqual(len(get_entities_vocabulary("t", "http://dir")), 0)
        with patch("imio.smartweb.common.utils.get_json", return_value={"items": []}):
            self.assertEqual(len(get_entities_vocabulary("t", "http://dir")), 0)

    # ------------------------------
    # translate_vocabulary_term (uncovered branches)
    # ------------------------------
    def test_translate_vocabulary_term_non_translated_vocabulary(self):
        # Topics is not in TRANSLATED_VOCABULARIES -> factory(portal) branch
        self.assertEqual(
            translate_vocabulary_term("imio.smartweb.vocabulary.Topics", "culture"),
            "Culture",
        )

    def test_translate_vocabulary_term_returns_empty_when_term_is_none(self):
        vocabulary = MagicMock()
        vocabulary.getTerm.return_value = None
        factory = MagicMock(return_value=vocabulary)
        with patch("imio.smartweb.common.utils.getUtility", return_value=factory):
            result = translate_vocabulary_term(
                "imio.smartweb.vocabulary.Topics", "whatever"
            )
        self.assertEqual(result, "")

    # ------------------------------
    # geocode_object (no location found)
    # ------------------------------
    def test_geocode_object_no_location_returns_false(self):
        obj = GeolocatedObject()
        obj.street = "Nowhere street"
        with patch("imio.smartweb.common.utils._geocode", return_value=None):
            self.assertFalse(geocode_object(obj))

    # ------------------------------
    # rich_description
    # ------------------------------
    def test_rich_description(self):
        result = rich_description("**bold** text\r\nsecond line")
        self.assertIn("<strong>bold</strong>", result)
        self.assertIn("<br/>", result)
        self.assertNotIn("\r\n", result)

    # ------------------------------
    # registry-backed flags
    # ------------------------------
    def test_is_log_active(self):
        self.assertFalse(is_log_active())
        with patch("plone.api.portal.get_registry_record", return_value=True):
            self.assertTrue(is_log_active())

    def test_activate_sending_data_to_odwb_for_staging(self):
        self.assertFalse(activate_sending_data_to_odwb_for_staging())
        with patch("plone.api.portal.get_registry_record", return_value=True):
            self.assertTrue(activate_sending_data_to_odwb_for_staging())

    # ------------------------------
    # is_staging_or_local
    # ------------------------------
    def _patch_portal_url(self, url):
        portal = SimpleNamespace(absolute_url=lambda: url)
        return patch("plone.api.portal.get", return_value=portal)

    def test_is_staging_or_local(self):
        cases = {
            "http://localhost:8080/plone": True,
            "http://127.0.0.1/plone": True,
            "https://staging.example.com": True,
            "https://preprod.example.com": True,
            "https://www.example.com": False,
            "http://nohost/plone": False,
        }
        for url, expected in cases.items():
            with self._patch_portal_url(url):
                self.assertEqual(is_staging_or_local(), expected, url)

    # ------------------------------
    # parent traversal helpers
    # ------------------------------
    def test_get_parent_providing(self):
        folder = api.content.create(container=self.portal, type="Folder", title="F")
        doc = api.content.create(container=folder, type="Document", title="D")
        # The site root is found walking up the acquisition chain
        self.assertTrue(
            IPloneSiteRoot.providedBy(get_parent_providing(doc, IPloneSiteRoot))
        )
        # No ancestor provides this marker -> None
        self.assertIsNone(get_parent_providing(doc, IMarkerNobodyProvides))

    def test_get_parent_of_type(self):
        folder = api.content.create(container=self.portal, type="Folder", title="F")
        doc = api.content.create(container=folder, type="Document", title="D")
        self.assertEqual(get_parent_of_type(doc, "Folder"), folder)
        self.assertIsNone(get_parent_of_type(doc, "NonExistentType"))

    # ------------------------------
    # image format helpers
    # ------------------------------
    def test_get_pil_mimetype(self):
        self.assertEqual(_get_pil_mimetype(SimpleNamespace(format="PNG")), "image/png")
        self.assertEqual(
            _get_pil_mimetype(SimpleNamespace(format="UNKNOWN")),
            "application/octet-stream",
        )

    def test_get_image_format_from_content_type(self):
        value = SimpleNamespace(contentType="image/png")
        self.assertEqual(get_image_format(value), "image/png")

    def test_get_image_format_detected_from_data(self):
        test_image = os.path.join(os.path.dirname(__file__), "resources/image.png")
        with open(test_image, "rb") as fd:
            data = fd.read()
        # No contentType attribute -> falls back to PIL detection
        self.assertEqual(get_image_format(SimpleNamespace(data=data)), "image/png")

    def test_get_image_format_invalid_data_returns_none(self):
        self.assertIsNone(get_image_format(SimpleNamespace(data=b"not an image")))
