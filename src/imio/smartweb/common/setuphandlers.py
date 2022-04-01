# -*- coding: utf-8 -*-

from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


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


def post_install(context):
    """Post install script"""
    acl_users = api.portal.get_tool("acl_users")
    session = acl_users.session
    # don't make cookie persistent across closing the browser
    session.cookie_lifetime = 0
    # set cookie validity to 8 hours
    session.timeout = 8 * 3600


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
