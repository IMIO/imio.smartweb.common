# -*- coding: utf-8 -*-

from Acquisition import aq_base
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.dexterity.textindexer.utils import searchable
from plone.resource.file import FilesystemFile
from Products.CMFPlone.resources import utils
from Products.CMFPlone.resources import webresource
from Products.CMFPlone.resources.utils import get_override_directory
from Products.CMFPlone.resources.utils import logger
from zExceptions import NotFound

searchable(ICategorization, "subjects")


def patched_get_resource(context, path):
    """
    Avoid errors with TTW theme resources
    See https://github.com/plone/Products.CMFPlone/issues/3705
    """
    if path.startswith("++plone++"):
        # ++plone++ resources can be customized, we return their override
        # value if any
        overrides = get_override_directory(context)
        filepath = path[9:]
        if overrides.isFile(filepath):
            return overrides.readFile(filepath)

    if "?" in path:
        # Example from plone.session:
        # "acl_users/session/refresh?session_refresh=true&type=css&minutes=5"
        # Traversing will not work then.  In this example we could split on "?"
        # and traverse to the first part, acl_users/session/refresh, but this
        # gives a function, and this fails when we call it below, missing a
        # REQUEST argument
        return
    try:
        resource = context.unrestrictedTraverse(path)
    except (NotFound, AttributeError, KeyError):
        logger.warning(
            f"Could not find resource {path}. You may have to create it first."
        )  # noqa
        return

    if isinstance(resource, FilesystemFile):
        (directory, sep, filename) = path.rpartition("/")
        return context.unrestrictedTraverse(directory).readFile(filename)

    # calling the resource may modify the header, i.e. the content-type.
    # we do not want this, so keep the original header intact.
    response_before = context.REQUEST.response
    context.REQUEST.response = response_before.__class__()
    if hasattr(aq_base(resource), "GET"):
        # for FileResource
        result = resource.GET()
    else:
        # any BrowserView
        try:
            # MONKEY IMIO: this avoids AttributeError: __call__ on resources
            result = resource()
        except AttributeError:
            if isinstance(resource.data, bytes):
                result = resource.data
            elif isinstance(resource.data.data, bytes):
                result = resource.data.data
    context.REQUEST.response = response_before
    return result


utils.get_resource = patched_get_resource
webresource.get_resource = patched_get_resource
