# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from collective.taxonomy.jsonimpl import ImportJson as baseImportJson
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from zope.component import queryUtility
from zope.i18n import translate

import json


class ImportJson(baseImportJson):
    """Update taxonomy using json data."""

    def __call__(self):
        request = self.request
        if request.method == "POST":
            data = json.loads(request.get("BODY", ""))
            taxonomy = queryUtility(ITaxonomy, name=data["taxonomy"])
            languages = data["languages"]
            items_to_check = []
            nodes = data["tree"]["subnodes"]
            for language in languages:
                for node in nodes:
                    if node["translations"].get(language):
                        items_to_check.append(
                            {node["key"]: node["translations"][language]}
                        )
                ids_remaining = [key for data in items_to_check for key in data.keys()]
                if not taxonomy.inverted_data.get(language):
                    continue
                initial_taxonomy_ids = [k for k in taxonomy.inverted_data[language]]
                for id in initial_taxonomy_ids:
                    if id in ids_remaining:
                        continue
                    # This is a removed term
                    catalog = api.portal.get_tool("portal_catalog")
                    brains = catalog.searchResults(
                        object_provides=taxonomy.getGeneratedName()
                    )
                    for brain in brains:
                        index_key = f"taxonomy_{taxonomy.getShortName()}"
                        if hasattr(brain, index_key) and id in getattr(
                            brain, index_key
                        ):
                            obj = brain.getObject()
                            here = obj.absolute_url()
                            term_title = taxonomy.translate(
                                id, context=obj, target_language=language
                            )
                            return json.dumps(
                                {
                                    "status": "error",
                                    "message": translate(
                                        _(
                                            'Term "${term_title}" can\'t be removed because it is used (at least) here : ${here}',
                                            mapping={
                                                "term_title": term_title,
                                                "here": here,
                                            },
                                        ),
                                        context=request,
                                    ),
                                }
                            )
        return super(ImportJson, self).__call__()
