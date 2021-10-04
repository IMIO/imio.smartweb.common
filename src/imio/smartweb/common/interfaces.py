# -*- coding: utf-8 -*-

from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IImioSmartwebCommonLayer(IDefaultPloneLayer, IPloneFormLayer):
    """Marker interface that defines a browser layer."""


class ICropping(Interface):
    def get_scales(fieldname, request=None):
        """Return the available cropping scales for a field on an object."""
