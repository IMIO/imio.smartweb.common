# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class ITopics(model.Schema):

    model.fieldset("categorization", label=_(u"Categorization"), fields=["topics"])
    topics = schema.List(
        title=_(u"Topics"),
        description=_(
            u"Important! Topics are used to filter search results and create lists"
        ),
        value_type=schema.Choice(vocabulary="imio.smartweb.vocabulary.Topics"),
        required=False,
    )
    directives.widget(topics=SelectFieldWidget)
