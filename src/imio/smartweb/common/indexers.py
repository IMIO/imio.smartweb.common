# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import parent


@indexer(IDexterityContent)
def breadcrumb(obj):
    if IPloneSiteRoot.providedBy(obj):
        return ""
    titles = [obj.title]
    while not IPloneSiteRoot.providedBy(parent(obj)):
        obj = parent(obj)
        titles.insert(0, obj.title)
    return " > ".join(titles)
