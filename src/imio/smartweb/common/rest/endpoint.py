# -*- coding: utf-8 -*-

from collections import Counter
from imio.smartweb.common.rest.utils import get_json
from plone import api
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized

import json
import logging

logger = logging.getLogger("imio.smartweb.common")


class FindEndpointHandler(SearchHandler):
    def search(self, query=None):
        results = {"items": []}
        portal = api.portal.get()
        get_types_url = f"{portal.absolute_url()}/@types"
        auth_header = self.request._orig_env.get("HTTP_AUTHORIZATION", None)
        types = get_json(get_types_url, auth=auth_header, timeout=20)
        if not types:
            raise Unauthorized("No types found, you are not allowed to search")
        self._constrain_query_by_path(query)
        if not query.get("path"):
            query["path"] = {"query": "/Plone"}
        # query = self._parse_query(query)
        if query.get("type_of_request") == "count_contents_types":
            results = self.count_contents_types(query)
        elif query.get("type_of_request") == "find_big_files_or_images":
            results = self.find_big_files_or_images(query)
        elif query.get("type_of_request") == "get_max_depth":
            results = self.get_max_depth()
        elif query.get("type_of_request") == "check_value_of_field":
            results = self.check_value_of_field(
                query.get("portal_type"),
                query.get("field_name"),
                query.get("expected_values"),
            )
        else:
            return super().search(query)
        return results

    def count_contents_types(self, query):
        results = {"items": []}
        if query.get("operator") == "and":
            query["path"]["depth"] = -1
            lazy_resultset = self.catalog.searchResults(**query)
            results = {
                "items": [
                    {
                        "portal_type": query.get("portal_type"),
                        "nb_items": len(lazy_resultset),
                    }
                ]
            }
        else:
            portal_types = (
                query.get("portal_type")
                if isinstance(query.get("portal_type"), list)
                else [query.get("portal_type")] if query.get("portal_type") else []
            )
            for portal_type in portal_types:
                new_query = query.copy()
                new_query["portal_type"] = portal_type
                lazy_resultset = self.catalog.searchResults(**new_query)
                results["items"].append(
                    {"portal_type": portal_type, "nb_items": len(lazy_resultset)}
                )
        # fullobjects = False
        # results = getMultiAdapter((lazy_resultset, self.request), ISerializeToJson)(
        #     fullobjects=fullobjects
        # )
        return results

    def find_big_files_or_images(self, query):
        SIZE_LIMIT = query.get("size", "1000000")
        results = {"items": []}
        lazy_resultset = self.catalog.searchResults(**query)
        for brain in lazy_resultset:
            obj = brain.getObject()
            blob = getattr(obj, "file", None) or getattr(obj, "image", None)
            if blob and hasattr(blob, "getSize"):
                size = blob.getSize()
                if size > int(SIZE_LIMIT):
                    results["items"].append(
                        {
                            "title": obj.title,
                            "portal_type": obj.portal_type,
                            "url": obj.absolute_url(),
                            "size": round(size / (1024 * 1024), 2),
                        }
                    )
        return results

    def get_max_depth(self):
        portal = api.portal.get()
        catalog = getToolByName(portal, "portal_catalog")

        max_depth = 0
        results = {"items": []}

        for brain in catalog():
            path = brain.getPath()
            depth = len(path.strip("/").split("/"))
            if depth > max_depth:
                max_depth = depth
                results["items"] = [{"path": path, "depth": depth}]
            elif depth == max_depth:
                results["items"].append({"path": path, "depth": depth})
        results["max_depth"] = max_depth
        return results

    def check_value_of_field(self, portal_type, field_name, expected_values):
        """
        Analyse la répartition des valeurs d'un champ dans les objets d'un content_type donné.
        query sample : http://localhost:8085/Plone/@find?portal_type=imio.events.Event&field_name=event_type&expected_values=["activity", "event-driven"]&type_of_request=check_value_of_field

        :param content_type: str, le portal_type (ex: "Event")
        :param field_name: str, field name (ex: "event_type")
        :param expected_values: list, list of values we want to check (ex: ["activity", "event-driven"])
        :return: dict {valeur: {"count": n, "percent": x.xx}}
        """
        brains = self.catalog(portal_type=portal_type)

        total = len(brains)
        if total == 0:
            return {}

        # Récupération et normalisation des valeurs
        values = []
        for brain in brains:
            obj = brain.getObject()
            value = getattr(obj, field_name, None)
            if isinstance(value, (list, tuple)):
                if not value:
                    # liste/tuple vide => on compte 1 None
                    values.append(None)
                else:
                    mapped = [
                        None if (v in ("", "None") or v is None) else v for v in value
                    ]
                    # si TOUT est None, on compte 1 None (au lieu d'en ajouter 0)
                    if all(v is None for v in mapped):
                        values.append(None)
                    else:
                        values.extend(mapped)
            else:
                v = None if (value in ("", "None") or value is None) else value
                values.append(v)
        counter = Counter(values)

        # Normalisation des valeurs attendues
        expected_values = normalize_query_param(expected_values)
        # On garde les labels originaux pour l'affichage, mais on mappe "None" vers None réel pour le compteur
        expected_mapping = {v: (None if v == "None" else v) for v in expected_values}

        # Calcul stats
        result = {}
        for label, key in expected_mapping.items():
            count = counter.get(key, 0)
            percent = (count / total) * 100 if total > 0 else 0
            result[label] = {"count": count, "percent": round(percent, 2)}

        return result


class FindEndpoint(Service):
    def reply(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return FindEndpointHandler(self.context, self.request).search(query)


def normalize_query_param(value):
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        val = value.strip()
        # Try to parse json list
        if val.startswith("[") and val.endswith("]"):
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return [val]
        else:
            return [val]
    return [value]
