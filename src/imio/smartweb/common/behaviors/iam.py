# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IAm(model.Schema):

    model.fieldset("categorization", label=_(u"Categorization"), fields=["iam"])
    iam = schema.List(
        title=_(u"I am"),
        description=_(u"Tell me who you are..."),
        value_type=schema.Choice(vocabulary="imio.smartweb.vocabulary.IAm"),
        required=False,
    )
    directives.widget(iam=SelectFieldWidget)
