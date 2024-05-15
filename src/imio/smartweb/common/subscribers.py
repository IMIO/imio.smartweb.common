# -*- coding: utf-8 -*-

from imio.smartweb.common.utils import clean_invisible_char
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.textfield.value import IRichTextValue
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from zope.lifecycleevent.interfaces import IAttributes
from zope.schema import getFields

import DateTime


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
    for schema in iterSchemata(obj):
        if (IFile).providedBy(obj) or (IImage).providedBy(obj):
            obj.setEffectiveDate(obj.created())
        for name, field in getFields(schema).items():
            value = getattr(obj, name)
            if IRichTextValue.providedBy(value):
                str = clean_invisible_char(value.raw)
                new_value = RichTextValue(
                    str,
                    mimeType=value.mimeType,
                    outputMimeType=value.outputMimeType,
                    encoding=value.encoding,
                )
                setattr(obj, name, new_value)
    reindex_breadcrumb(obj, event)


def modified_content(obj, event):
    for schema in iterSchemata(obj):
        for name, field in getFields(schema).items():
            value = getattr(obj, name, None)
            if value is None:
                continue
            if IRichTextValue.providedBy(value):
                str = clean_invisible_char(value.raw)
                new_value = RichTextValue(
                    str,
                    mimeType=value.mimeType,
                    outputMimeType=value.outputMimeType,
                    encoding=value.encoding,
                )
                setattr(obj, name, new_value)
    reindex_breadcrumb(obj, event)


def modified_cropping(obj, event):
    now = DateTime.DateTime()
    obj.setModificationDate(now)
    obj.reindexObject(idxs=["modified"])
