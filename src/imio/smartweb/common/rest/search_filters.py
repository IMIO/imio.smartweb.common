# -*- coding: utf-8 -*-

from imio.smartweb.common.config import VOCABULARIES_MAPPING
from imio.smartweb.common.rest.utils import get_restapi_query_lang
from imio.smartweb.common.utils import get_term_from_vocabulary
from operator import itemgetter
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter


# we don't need some brains metadata to construct search filters
EXCLUDED_METADATA = [
    "container_uid",
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

    ignored_params = ["fullobjects", "b_size", "b_start"]

    def search(self, query=None):
        if query is None:
            query = {}

        for param in self.ignored_params:
            if param in query:
                del query[param]

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

        lang = get_restapi_query_lang(query)
        local_categories_trans = {}

        metadatas = list(set(metadatas) - set(EXCLUDED_METADATA))
        filters = {metadata: set() for metadata in metadatas}
        for brain in brains:
            for metadata in metadatas:
                value = getattr(brain, metadata, None)
                if not value:
                    continue
                if not isinstance(value, (list, tuple)):
                    value = [value]
                for v in value:
                    filters[metadata].add(v)
                    if metadata == "local_category":
                        local_categories_trans[v] = getattr(
                            brain, f"{metadata}_{lang}", v
                        )

        results = {}
        for metadata, values in filters.items():
            results[metadata] = []
            if metadata in VOCABULARIES_MAPPING:
                for v in values:
                    term = get_term_from_vocabulary(VOCABULARIES_MAPPING[metadata], v)
                    title = term.title
                    serializer = getMultiAdapter(
                        (term, self.request), interface=ISerializeToJson
                    )
                    term = serializer()
                    term["title"] = json_compatible(title)  # needed for translations
                    results[metadata].append(term)
            elif metadata == "local_category":
                results[metadata] = [
                    {"token": v, "title": local_categories_trans[v]} for v in values
                ]
            else:
                results[metadata] = [{"token": v, "title": v} for v in values]
            results[metadata].sort(key=itemgetter("title"))

        return results
