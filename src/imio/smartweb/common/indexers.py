# -*- coding: utf-8 -*-

from Acquisition import aq_base
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import parent
from Products.CMFPlone.utils import safe_hasattr


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
        # we have a lead image on the object
        return True
    if safe_hasattr(aq_base(obj), "image", None):
        # we have an image field on the object, ex: for Image content type
        return True
    return False
