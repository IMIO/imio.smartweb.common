# -*- coding: utf-8 -*-

from plone import api
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.imagecropping.interfaces import IImageCroppingMarker
from zope.annotation.interfaces import IAnnotations

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
    brains = api.content.find(object_provides=IImageCroppingMarker)
    scales_to_delete = [
        "affiche",
        "extralarge",
        "large" "slide",
        "medium",
        "preview",
        "vignette",
        "mini",
        "liste",
        "thumb",
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
