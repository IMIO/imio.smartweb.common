# -*- coding: utf-8 -*-

from collective.dexteritytextindexer.utils import searchable
from plone.app.dexterity.behaviors.metadata import ICategorization

searchable(ICategorization, "subjects")
