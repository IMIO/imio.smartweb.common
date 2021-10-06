# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.supermodel import model
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IImioSmartwebCommonLayer(IDefaultPloneLayer, IPloneFormLayer):
    """Marker interface that defines a browser layer."""


class ICropping(Interface):
    def get_scales(fieldname, request=None):
        """Return the available cropping scales for a field on an object."""


class IAddress(model.Schema):

    model.fieldset(
        "address",
        label=_(u"Address"),
        fields=["street", "number", "complement", "zipcode", "city", "country"],
    )
    street = schema.TextLine(title=_(u"Street"), required=False)
    number = schema.TextLine(title=_(u"Number"), required=False)
    complement = schema.TextLine(title=_(u"Complement"), required=False)
    zipcode = schema.Int(title=_(u"Zipcode"), required=False)
    city = schema.TextLine(title=_(u"City"), required=False)
    country = schema.Choice(
        title=_(u"Country"),
        source="imio.smartweb.vocabulary.Countries",
        required=False,
    )
