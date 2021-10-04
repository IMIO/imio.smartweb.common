# -*- coding: utf-8 -*-

from plone.namedfile.interfaces import IAvailableSizes
from zope.component import getUtility


class BaseCroppingProvider(object):
    def __init__(self, context):
        self.context = context

    def get_scales(self, fieldname, request=None):
        allowed_sizes = getUtility(IAvailableSizes)()
        scales = list(allowed_sizes.keys())
        if fieldname == "image":
            # scales used for lead image field
            scales.remove("banner")
        return scales
