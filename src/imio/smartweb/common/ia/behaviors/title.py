# -*- coding: utf-8 -*-

from imio.smartweb.common.ia.widgets.widget import SuggestedIATitlesFieldWidget
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IIASmartTitle(IBasic):
    """Behavior qui remplace le titre standard par un titre avec IA"""

    directives.widget(title=SuggestedIATitlesFieldWidget)
    title = schema.TextLine(title=_("Title"), required=True)
