# -*- coding: utf-8 -*-

from plone.namedfile.interfaces import IAvailableSizes
from zope.component import getUtility


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
