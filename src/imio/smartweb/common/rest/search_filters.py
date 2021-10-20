# -*- coding: utf-8 -*-

from imio.smartweb.common.config import VOCABULARIES_MAPPING
from imio.smartweb.common.utils import get_term_from_vocabulary
from operator import itemgetter
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter


# we don't need some brains metadata to construct search filters
EXCLUDED_METADATA = [
    "effective",
    "end",
    "has_leadimage",
    "start",
    "UID",
]


class SearchFiltersGet(Service):
    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return SearchFiltersHandler(self.context, self.request).search(query)


class SearchFiltersHandler(SearchHandler):
    """
    Executes a catalog search based on a query dict, and returns the metadata
    values as vocabularies terms in JSON. This is used for example for smartweb
    faceted searches.
    """

    def search(self, query=None):
        if query is None:
            query = {}
        if "fullobjects" in query:
            del query["fullobjects"]

        use_site_search_settings = False
        if "use_site_search_settings" in query:
            use_site_search_settings = True
            del query["use_site_search_settings"]

        if use_site_search_settings:
            query = self.filter_query(query)

        self._constrain_query_by_path(query)
        query = self._parse_query(query)

        if "metadata_fields" not in query:
            return {}

        brains = self.catalog.searchResults(**query)

        metadatas = query["metadata_fields"]
        if not isinstance(metadatas, list):
            metadatas = [metadatas]

        metadatas = list(set(metadatas) - set(EXCLUDED_METADATA))
        filters = {metadata: set() for metadata in metadatas}
        for brain in brains:
            for metadata in metadatas:
                value = getattr(brain, metadata, None)
                if not value:
                    continue
                if isinstance(value, list) or isinstance(value, tuple):
                    for v in value:
                        filters[metadata].add(v)
                else:
                    filters[metadata].add(value)

        results = {}
        for metadata, values in filters.items():
            results[metadata] = []
            if metadata in VOCABULARIES_MAPPING:
                for v in values:
                    term = get_term_from_vocabulary(VOCABULARIES_MAPPING[metadata], v)
                    serializer = getMultiAdapter(
                        (term, self.request), interface=ISerializeToJson
                    )
                    term = serializer()
                    results[metadata].append(term)
                    results[metadata].sort(key=itemgetter("title"))
            else:
                results[metadata] = [{"token": v, "title": v} for v in sorted(values)]

        return results
