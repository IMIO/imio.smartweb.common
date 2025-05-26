# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from io import BytesIO
from imio.smartweb.common.config import TRANSLATED_VOCABULARIES
from imio.smartweb.common.interfaces import ICropping
from imio.smartweb.locales import SmartwebMessageFactory as _
from PIL import Image
from plone import api
from plone.app.imagecropping.storage import Storage
from plone.dexterity.utils import iterSchemata
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IAvailableSizes
from urllib.parse import urlparse
from zope.component import getUtility
from zope.i18n import translate
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm

import geopy
import re
import unicodedata


def get_vocabulary(voc_name):
    factory = getUtility(IVocabularyFactory, voc_name)
    vocabulary = factory(api.portal.get())
    return vocabulary


def get_term_from_vocabulary(vocabulary, value):
    portal = api.portal.get()
    factory = getUtility(IVocabularyFactory, vocabulary)
    vocabulary = factory(portal)
    try:
        term = vocabulary.getTerm(value)
    except LookupError:
        return SimpleTerm(value=value, title=value)
    return term


def translate_vocabulary_term(vocabulary, term, lang=None):
    if term is None:
        return ""
    portal = api.portal.get()
    factory = getUtility(IVocabularyFactory, vocabulary)
    if vocabulary in TRANSLATED_VOCABULARIES:
        vocabulary = factory(portal, lang=lang)
    else:
        vocabulary = factory(portal)
    term = vocabulary.getTerm(term)
    if term is None:
        return ""
    if lang is None:
        lang = api.portal.get_current_language()[:2]
    return translate(term.title, target_language=lang)


def geocode_object(obj):
    street_parts = [
        obj.number and str(obj.number) or "",
        obj.street,
        obj.complement,
    ]
    street = " ".join(filter(None, street_parts))
    entity_parts = [
        obj.zipcode and str(obj.zipcode) or "",
        obj.city,
    ]
    entity = " ".join(filter(None, entity_parts))
    country = translate_vocabulary_term(
        "imio.smartweb.vocabulary.Countries", obj.country
    )
    address = " ".join(filter(None, [street, entity, country]))
    if not address:
        return
    geolocator = geopy.geocoders.Nominatim(user_agent="contact@imio.be", timeout=3)
    location = geolocator.geocode(address)
    if location:
        obj.geolocation = Geolocation(
            latitude=location.latitude, longitude=location.longitude
        )
        obj.reindexObject(idxs=["longitude", "latitude"])
        return True
    return False


def rich_description(description):
    # **strong**
    description = re.sub(r"\*\*([^\*\*]*)\*\*", r"<strong>\1</strong>", description)
    # <br/>
    description = "<br/>".join(description.split("\r\n"))
    return description


def get_uncroppable_scales_infos(image, available_sizes, scales):
    img_height = image._height
    img_width = image._width
    result = {}
    uncroppable_scales = set()
    min_height = min_width = 0
    for scale in scales:
        width, height = available_sizes.get(scale)
        if 65536 > width > img_width or 65536 > height > img_height:
            uncroppable_scales.add(scale)
        if 65536 > width > min_width:
            min_width = width
        if 65536 > height > min_height:
            min_height = height
    if uncroppable_scales:
        result = {
            "scales": sorted(list(uncroppable_scales)),
            "min_height": str(min_height),
            "min_width": str(min_width),
            "height": str(img_height),
            "width": str(img_width),
        }
    return result


def show_warning_for_scales(obj, request):
    if not api.user.has_permission("Modify portal content", obj=obj):
        return
    available_sizes = getUtility(IAvailableSizes)() or {}
    cropping_scales_adapter = ICropping(obj, alternate=None)
    for schema in iterSchemata(obj):
        for name, field in getFields(schema).items():
            if type(field) is not NamedBlobImage or not getattr(obj, name, None):
                continue
            field_scales = cropping_scales_adapter.get_scales(name, request)
            uncroppable_infos = get_uncroppable_scales_infos(
                getattr(obj, name), available_sizes, field_scales
            )
            if not uncroppable_infos:
                continue
            api.portal.show_message(
                _(
                    'The image uploaded in the "${field_title}" field may be '
                    "degraded because it does not meet the required minimum dimensions of "
                    "${min_width}px width by ${min_height}px height "
                    "(uploaded image size: ${width}px width by ${height}px height). "
                    "You can see the detail via the Cropping menu.",
                    mapping={
                        "field_title": field.title,
                        "min_height": uncroppable_infos["min_height"],
                        "min_width": uncroppable_infos["min_width"],
                        "height": uncroppable_infos["height"],
                        "width": uncroppable_infos["width"],
                    },
                ),
                request=request,
                type="warning",
            )


def remove_cropping(obj, field_name, scales):
    storage = Storage(obj)
    for scale in scales:
        storage.remove(field_name, scale)


def clean_invisible_char(value):
    # surpassing all control characters
    # checking for starting with C
    if value is None:
        return value
    res = "".join(char for char in value if unicodedata.category(char)[0] != "C")
    return res


def is_log_active():
    return api.portal.get_registry_record("imio.smartweb.common.log", default=False)


# todo: create staging/prod env var. instead of using parsed_url
def is_staging_or_local():
    portal = api.portal.get()
    portal_url = portal.absolute_url()
    parsed_url = urlparse(portal_url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    elem = ["localhost", "127.0.0.1"]
    pattern = "|".join(map(re.escape, elem))
    if scheme == "http" and re.search(pattern, netloc):
        return True
    elif scheme == "https" and "staging" in netloc:
        return True
    else:
        return False


def activate_sending_data_to_odwb_for_staging():
    return api.portal.get_registry_record(
        "imio.smartweb.common.activate_sending_data_to_odwb_for_staging", default=False
    )


def get_parent_of_type(context, content_type):
    # Traverse up the hierarchy until we find an object with the specified content type
    parent = context
    while parent is not None:
        if getattr(parent, "portal_type", None) == content_type:
            return parent
        parent = aq_parent(parent)
    return None


def _get_pil_mimetype(pil_image):
    """Retourne le MIME type d'une image PIL."""
    format_to_mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "GIF": "image/gif",
        "BMP": "image/bmp",
        "TIFF": "image/tiff",
        "WEBP": "image/webp",
        "SVG": "image/svg+xml",
    }
    return format_to_mime.get(pil_image.format, "application/octet-stream")


def get_image_format(named_blob_image):
    """Détecte le format d'une image à partir de son contenu binaire."""
    if hasattr(named_blob_image, "contentType"):
        return named_blob_image.contentType
    if named_blob_image and named_blob_image.data:
        try:
            with Image.open(BytesIO(named_blob_image.data)) as img:
                return _get_pil_mimetype(img)
        except Exception:
            return None
