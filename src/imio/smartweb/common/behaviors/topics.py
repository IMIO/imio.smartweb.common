# -*- coding: utf-8 -*-

from imio.smartweb.common.widgets.select import TranslatedAjaxSelectFieldWidget
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class ITopics(model.Schema):
    model.fieldset("categorization", label=_("Categorization"), fields=["topics"])
    topics = schema.List(
        title=_("Topics"),
        description=_(
            "Important! Topics are used to filter search results and create lists"
        ),
        value_type=schema.Choice(vocabulary="imio.smartweb.vocabulary.Topics"),
        default=[],
        required=False,
    )
    directives.widget(topics=TranslatedAjaxSelectFieldWidget)
