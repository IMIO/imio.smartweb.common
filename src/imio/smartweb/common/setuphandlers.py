# -*- coding: utf-8 -*-

from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import logging
import os

logger = logging.getLogger("imio.smartweb.common")


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "imio.smartweb.common:testing",
            "imio.smartweb.common:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide unwanted products from site-creation and quickinstaller."""
        return [
            "imio.smartweb.common.upgrades",
        ]


def set_omnia_core_settings():
    """Pre-fill the imio.omnia.core control panel fields (application_id and
    organization_id) from the legacy SmartWeb environment variables, unless
    they are already set."""
    try:
        from imio.omnia.core.settings import get_application_id
        from imio.omnia.core.settings import get_organization_id
        from imio.omnia.core.settings import set_application_id
        from imio.omnia.core.settings import set_organization_id

        if not get_application_id():
            set_application_id(os.environ.get("application_id", "iA.Smartweb"))
        if not get_organization_id():
            set_organization_id(os.environ.get("PROJECT_ID", "smartweb"))
    except Exception:
        logger.warning("Could not pre-fill imio.omnia.core IA settings", exc_info=True)


def post_install(context):
    """Post install script"""
    acl_users = api.portal.get_tool("acl_users")
    session = acl_users.session
    # don't make cookie persistent across closing the browser
    session.cookie_lifetime = 0
    # set cookie validity to 8 hours
    session.timeout = 8 * 3600
    set_omnia_core_settings()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
