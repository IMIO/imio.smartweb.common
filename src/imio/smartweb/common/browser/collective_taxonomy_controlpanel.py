# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from collective.taxonomy.jsonimpl import EditTaxonomyData as baseEditTaxonomyData
from plone import api
from zope.component import queryUtility
from Products.Five import BrowserView


import json


class EditTaxonomyData(baseEditTaxonomyData, BrowserView):
    """Edit taxonomy data."""


class DeleteTaxonomyData(BrowserView):

    def check_delete_taxonomy(self):
        body = self.request.get("BODY", b"{}")  # Récupération du corps de la requête
        data = json.loads(body)  # Décodage du JSON
        term_id = data.get("termId")  # Extraction de l'ID
        result = {term_id} if term_id else set()
        taxonomy = queryUtility(ITaxonomy, name="collective.taxonomy.contact_category")
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(object_provides=taxonomy.getGeneratedName())
        # On parcours tous les brains pour lesquels la taxonomie est utilisée
        for brain in brains:
            index_key = f"taxonomy_{taxonomy.getShortName()}"
            if hasattr(brain, index_key):
                set2 = set(getattr(brain, index_key))
                if result & set2:
                    obj = brain.getObject()
                    url = obj.absolute_url()
                    title = obj.Title()
                    return json.dumps(
                        {
                            "status": "error",
                            "message": f'<h2>Impossible de supprimer ce terme.</h2><p>Ce terme est au moins utilisé ici : <a href="{url}" target="_blank" title="{title}">{url}</a></p>',
                        }
                    )
        return json.dumps({"status": "success", "message": "Suppression autorisée"})
