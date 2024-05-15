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
    model.fieldset("categorization", label=_("Categorization"), fields=["iam"])
    iam = schema.List(
        title=_("I am"),
        description=_(
            "Important! These categories are used to create lists accessible via the navigation menu"
        ),
        value_type=schema.Choice(vocabulary="imio.smartweb.vocabulary.IAm"),
        default=[],
        required=False,
    )
    directives.widget(iam=SelectFieldWidget)
