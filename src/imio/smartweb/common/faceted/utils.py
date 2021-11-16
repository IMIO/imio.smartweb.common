# -*- coding: utf-8 -*-

from eea.facetednavigation.subtypes.interfaces import IPossibleFacetedNavigable
from zope.globalrequest import getRequest


def configure_faceted(obj, faceted_config_path):
    if not IPossibleFacetedNavigable.providedBy(obj):
        return
    subtyper = obj.restrictedTraverse("@@faceted_subtyper")
    if not subtyper:
        return
    subtyper.enable()
    with open(faceted_config_path, "rb") as faceted_config:
        obj.unrestrictedTraverse("@@faceted_exportimport").import_xml(
            import_file=faceted_config
        )
    request = getRequest()
    request.response.redirect(obj.absolute_url())
