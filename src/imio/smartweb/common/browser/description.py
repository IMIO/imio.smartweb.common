# -*- coding: utf-8 -*-

from imio.smartweb.common.utils import rich_description
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView


class RichDescription(BrowserView):
    def description(self):
        """Description with html carriage return and bold"""
        description = ""
        if base_hasattr(self.context, "description"):
            description = self.context.description or ""
        description = rich_description(description)
        return description
