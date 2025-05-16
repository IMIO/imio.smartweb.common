# -*- coding: utf-8 -*-

from collective.privacy.interfaces import ICollectivePrivacyLayer
from collective.taxonomy.interfaces import IBrowserLayer
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.supermodel import model
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IImioSmartwebCommonLayer(
    IBrowserLayer, IDefaultPloneLayer, IPloneFormLayer, ICollectivePrivacyLayer
):
    """Marker interface that defines a browser layer."""


class ILocalManagerAware(Interface):
    """Marker interface that allows a local management."""


class ICropping(Interface):
    def get_scales(fieldname, request=None):
        """Return the available cropping scales for a field on an object."""


class IAddress(model.Schema):
    model.fieldset(
        "address",
        label=_("Address"),
        fields=["street", "number", "complement", "zipcode", "city", "country"],
    )
    street = schema.TextLine(title=_("Street"), required=False)
    number = schema.TextLine(title=_("Number"), required=False)
    complement = schema.TextLine(title=_("Complement"), required=False)
    zipcode = schema.Int(title=_("Zipcode"), required=False)
    city = schema.TextLine(title=_("City"), required=False)
    country = schema.Choice(
        title=_("Country"),
        source="imio.smartweb.vocabulary.Countries",
        required=False,
    )


class ITranslatedAjaxSelectWidget(IAjaxSelectWidget):
    """Marker interface for the TranslatedAjaxSelectWidget."""
