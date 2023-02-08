# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import ILocalManagerAware
from imio.smartweb.common.sharing import permissions
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implementer


@implementer(ISharingPageRole)
class LocalManagerRole(object):
    title = _("Can manage locally")
    required_permission = permissions.DelegateLocalManagerRole
    required_interface = ILocalManagerAware
