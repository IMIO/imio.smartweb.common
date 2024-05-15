# -*- coding: utf-8 -*-

from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.imagecropping.interfaces import IImageCroppingMarker
from plone.app.textfield.value import IRichTextValue
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from zope.annotation.interfaces import IAnnotations
from zope.schema import getFields

import logging

logger = logging.getLogger("imio.smartweb.common")
PROFILEID = "profile-imio.smartweb.common:default"


def reload_registry(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runImportStepFromProfile(PROFILEID, "plone.app.registry")


def reload_actions(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runImportStepFromProfile(PROFILEID, "actions")


def reindex_searchable_text(context):
    portal_catalog = api.portal.get_tool("portal_catalog")
    portal_catalog.manage_reindexIndex(ids=["SearchableText"])
    logger.info("Reindexed SearchableText index")


def upgrade_barceloneta(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.upgradeProfile("plonetheme.barceloneta:default")


def remove_deprecated_cropping_annotations(context):
    with api.env.adopt_user(username="admin"):
        brains = api.content.find(object_provides=IImageCroppingMarker)
        scales_to_delete = [
            "affiche",
            "extralarge",
            "slide",
            "medium",
            "vignette",
            "liste",
        ]
        for brain in brains:
            obj = brain.getObject()
            annotations = IAnnotations(obj)
            scales = annotations.get(PAI_STORAGE_KEY)
            if scales is None:
                continue
            deleted_scales = []
            for scale in scales:
                scale_name = scale.split("_")[-1]
                if scale_name in scales_to_delete:
                    deleted_scales.append(scale)

            for scale in deleted_scales:
                del scales[scale]
            if deleted_scales:
                obj.reindexObject()
                logger.info(
                    f'Remove deprecated scales : {",".join(deleted_scales)} cropping annotation on {obj.absolute_url()}'
                )


def restore_textfields_mimetypes(context):
    with api.env.adopt_user(username="admin"):
        brains = api.content.find(
            portal_type=[
                "imio.events.Event",
                "imio.news.NewsItem",
                "imio.smartweb.CirkwiView",
                "imio.smartweb.DirectoryView",
                "imio.smartweb.SectionText",
            ]
        )
        for brain in brains:
            obj = brain.getObject()
            for schema in iterSchemata(obj):
                for name, field in getFields(schema).items():
                    value = getattr(obj, name)
                    if not IRichTextValue.providedBy(value):
                        continue
                    new_value = RichTextValue(
                        value.raw,
                        mimeType="text/html",
                        outputMimeType="text/x-html-safe",
                        encoding="utf-8",
                    )
                    setattr(obj, name, new_value)
                    logger.info(
                        f"Fixed WYSIWYG field mimetypes on {obj.absolute_url()}"
                    )


def fix_missing_values_for_lists(context):
    catalog = api.portal.get_tool("portal_catalog")
    with api.env.adopt_user(username="admin"):
        brains = api.content.find(
            portal_type=[
                "File",
                "imio.directory.Contact",
                "imio.events.Event",
                "imio.news.NewsItem",
                "imio.smartweb.CirkwiView",
                "imio.smartweb.DirectoryView",
                "imio.smartweb.EventsView",
                "imio.smartweb.NewsView",
                "imio.smartweb.Page",
                "imio.smartweb.PortalPage",
                "imio.smartweb.Procedure",
                "imio.smartweb.SectionExternalContent",
                "imio.smartweb.SectionGallery",
                "imio.smartweb.SectionVideo",
            ]
        )
        for brain in brains:
            obj = brain.getObject()
            if hasattr(obj, "topics") and obj.topics is None:
                obj.topics = []
                catalog.catalog_object(obj, idxs=["topics"])
                logger.info(f"Fixed None list for Topics on {obj.absolute_url()}")
            if hasattr(obj, "iam") and obj.iam is None:
                obj.iam = []
                catalog.catalog_object(obj, idxs=["iam"])
                logger.info(f"Fixed None list for Iam on {obj.absolute_url()}")


def set_effective_date_equal_to_created_date(context):
    """Image and File content types have no workflow
    So, effective date was 1969/12/31 00:00:00 GMT+1"""

    with api.env.adopt_user(username="admin"):
        brains = api.content.find(
            portal_type=[
                "File",
                "Image",
            ]
        )
        for brain in brains:
            obj = brain.getObject()
            obj.setEffectiveDate(obj.created())
            obj.reindexObject(idxs=["effective"])


def reindex_solr(context):
    portal = api.portal.get()
    maintenance = portal.unrestrictedTraverse("@@solr-maintenance")
    maintenance.clear()
    maintenance.reindex()
