# -*- coding: utf-8 -*-

from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.dexterity.textindexer.utils import searchable

searchable(ICategorization, "subjects")
