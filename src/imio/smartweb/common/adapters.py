# -*- coding: utf-8 -*-

from imio.smartweb.common.utils import get_image_format
from plone.namedfile.interfaces import IAvailableSizes
from plone.namedfile.interfaces import INamedImageField
from plone.namedfile.field import InvalidImageFile
from zope.component import adapter
from zope.component import getUtility
from zope.interface import Interface


class BaseCroppingProvider(object):
    def __init__(self, context):
        self.context = context

    def get_scales(self, fieldname, request=None):
        if self.context.portal_type == "Image":
            # imio.smartweb.core override get_scales.
            # so this is only available for authentic sources
            return []
        allowed_sizes = getUtility(IAvailableSizes)()
        scales = list(allowed_sizes.keys())
        scales.remove("banner")
        return scales


@adapter(INamedImageField, Interface)
class ImageContenttypeValidator:
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __call__(self):
        return self.validate_image()

    def validate_image(self):
        if self.value is None:
            return False
        mimetype = get_image_format(self.value)

        valid_mimetypes = {
            "image/gif",
            "image/jpeg",
            "image/png",
            "image/svg+xml",
            "image/webp",
        }
        if mimetype not in valid_mimetypes:
            raise InvalidImageFile(mimetype, self.field.__name__)
        return True
