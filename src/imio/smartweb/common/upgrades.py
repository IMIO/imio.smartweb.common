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
