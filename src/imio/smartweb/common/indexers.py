# -*- coding: utf-8 -*-

from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import parent


@indexer(IDexterityContent)
def description(obj):
    if obj.description is None:
        return ""
    return obj.description.replace("**", "")


@indexer(IDexterityContent)
def breadcrumb(obj):
    if IPloneSiteRoot.providedBy(obj):
        return ""
    titles = [obj.title]
    while not IPloneSiteRoot.providedBy(parent(obj)):
        obj = parent(obj)
        titles.insert(0, obj.title)
    return " » ".join(titles)


@indexer(IDexterityContent)
def has_leadimage(obj):
    if ILeadImage.providedBy(obj) and getattr(obj, "image", False):
        return True
    return False
