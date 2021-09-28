# -*- coding: utf-8 -*-

from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
from zope.lifecycleevent.interfaces import IAttributes


def reindex_breadcrumb(obj, event):
    if not hasattr(event, "descriptions") or not event.descriptions:
        return

    for d in event.descriptions:
        if not IAttributes.providedBy(d):
            # we do not have fields change description, but maybe a request
            continue
        if d.interface is not IBasic:
            continue
        if "IBasic.title" in d.attributes:
            brains = api.content.find(context=obj)
            for brain in brains:
                content = brain.getObject()
                content.reindexObject(idxs=["breadcrumb"])
            return


def added_content(obj, event):
    reindex_breadcrumb(obj, event)


def modified_content(obj, event):
    reindex_breadcrumb(obj, event)
