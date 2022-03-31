# -*- coding: utf-8 -*-

from plone import api
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
