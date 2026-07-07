# -*- coding: utf-8 -*-
from DateTime import DateTime
from imio.smartweb.common.rest.endpoint import FindEndpoint
from imio.smartweb.common.rest.endpoint import FindEndpointHandler
from imio.smartweb.common.rest.endpoint import normalize_query_param
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile, NamedBlobImage
from unittest.mock import MagicMock
from unittest.mock import patch
from zExceptions import Unauthorized

import json
import unittest

# Minimal truthy @types payload: the endpoint only checks it is non-empty.
FAKE_TYPES = [{"id": "Document", "title": "Document"}]


class TestRestEndpoint(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # Simule un header d'auth présent dans la requête
        self.request._orig_env = {"HTTP_AUTHORIZATION": "Bearer TEST"}
        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
        )
        self.doc1 = api.content.create(
            container=self.folder, type="Document", title="Doc 1"
        )
        self.doc2 = api.content.create(
            container=self.folder, type="Document", title="Doc 2"
        )
        self.page = api.content.create(
            container=self.folder, type="Document", title="Doc 3"
        )

    def test_no_types(self):
        query = {
            "type_of_request": "count_contents_types",
            "portal_type": "Document",
            "path": {"query": self.portal.absolute_url_path()},
            "operator": "and",
        }
        handler = FindEndpointHandler(self.portal, self.request)
        self.assertRaises(Unauthorized, handler.search, query)

    # ------------------------------
    # count_contents_types
    # ------------------------------
    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_count_contents_types_operator_and(self, mjson):
        mjson.return_value = [
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/Document",
                "addable": "false",
                "id": "Document",
                "immediately_addable": "false",
                "title": "Document",
            }
        ]
        handler = FindEndpointHandler(self.portal, self.request)
        query = {
            "type_of_request": "count_contents_types",
            "portal_type": "Document",
            "path": {"query": self.portal.absolute_url_path()},
            "operator": "and",
        }
        res = handler.search(query)
        self.assertEqual(res, {"items": [{"portal_type": "Document", "nb_items": 3}]})

        # Test without path in query.
        # Path is automaticaly set.
        query = {
            "type_of_request": "count_contents_types",
            "portal_type": "Document",
            "operator": "and",
        }
        res = handler.search(query)
        self.assertEqual(res, {"items": [{"portal_type": "Document", "nb_items": 3}]})

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_count_contents_types_operator_or_multiple_types(self, mjson):
        mjson.return_value = [
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/Document",
                "addable": "false",
                "id": "Document",
                "immediately_addable": "false",
                "title": "Document",
            },
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/Folder",
                "addable": "false",
                "id": "Folder",
                "immediately_addable": "false",
                "title": "Folder",
            },
        ]
        handler = FindEndpointHandler(self.portal, self.request)
        query = {
            "type_of_request": "count_contents_types",
            "portal_type": ["Document", "Folder"],
            "path": {"query": self.portal.absolute_url_path()},
            "operator": "and",
        }
        res = handler.search(query)
        self.assertEqual(
            res, {"items": [{"portal_type": ["Document", "Folder"], "nb_items": 4}]}
        )

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_get_max_depth(self, mjson):
        mjson.return_value = [
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/Document",
                "addable": "false",
                "id": "Document",
                "immediately_addable": "false",
                "title": "Document",
            }
        ]
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search({"type_of_request": "get_max_depth"})
        self.assertEqual(res["max_depth"], 3)

        paths = {i["path"] for i in res["items"]}
        self.assertEqual(
            paths, {"/plone/folder/doc-2", "/plone/folder/doc-3", "/plone/folder/doc-1"}
        )

        folder2 = api.content.create(
            container=self.folder,
            type="Folder",
            title="Folder 2",
        )

        api.content.create(
            container=folder2,
            type="Document",
            title="Kamoulox",
        )
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search({"type_of_request": "get_max_depth"})
        self.assertEqual(res["max_depth"], 4)

        paths = {i["path"] for i in res["items"]}
        self.assertEqual(paths, {"/plone/folder/folder-2/kamoulox"})

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_check_value_of_field_counts_and_percents(self, mjson):
        mjson.return_value = [
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/Document",
                "addable": "false",
                "id": "Document",
                "immediately_addable": "false",
                "title": "Document",
            }
        ]
        api.content.create(
            container=self.folder,
            type="Document",
            title="Doc 2",
        )
        handler = FindEndpointHandler(self.portal, self.request)
        q = {
            "type_of_request": "check_value_of_field",
            "portal_type": "Document",
            "field_name": "title",
            "expected_values": ["Doc 1", "Doc 2", "Doc 3"],
        }
        res = handler.search(q)
        # Number
        self.assertEqual(res["Doc 1"]["count"], 1)
        self.assertEqual(res["Doc 2"]["count"], 2)
        self.assertEqual(res["Doc 3"]["count"], 1)

        # Pourcentages
        self.assertEqual(res["Doc 1"]["percent"], round(1 / 4 * 100, 2))  # 25%
        self.assertEqual(res["Doc 2"]["percent"], round(2 / 4 * 100, 2))  # 50%
        self.assertEqual(res["Doc 3"]["percent"], round(1 / 4 * 100, 2))  # 25%

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_find_big_files_or_images(self, mjson):
        mjson.return_value = [
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/Image",
                "addable": "false",
                "id": "Image",
                "immediately_addable": "false",
                "title": "Image",
            },
            {
                "@id": f"https://{self.portal.absolute_url()}/@types/File",
                "addable": "false",
                "id": "File",
                "immediately_addable": "false",
                "title": "File",
            },
        ]
        api.content.create(
            container=self.folder,
            type="File",
            id="bigfile",
            title="Big file",
            file=NamedBlobFile(data=b"x" * 2500000, filename="big.pdf"),  # 2,5 Mo
        )

        api.content.create(
            container=self.folder,
            type="Image",
            id="smallimage",
            title="Small image",
            image=NamedBlobImage(data=b"x" * 100000, filename="small.jpg"),  # 0,1 Mo
        )

        api.content.create(
            container=self.folder,
            type="Image",
            id="bigimage",
            title="Big image",
            image=NamedBlobImage(data=b"x" * 3100000, filename="big.jpg"),  # 3,1 Mo
        )
        handler = FindEndpointHandler(self.portal, self.request)
        q = {
            "type_of_request": "find_big_files_or_images",
            "portal_type": ["Image", "File"],
            "size": 1000000,
        }
        res = handler.search(q)
        # On attend seulement les gros
        titles = [it["title"] for it in res["items"]]
        self.assertEqual(set(titles), {"Big file", "Big image"})
        # Vérifie calcul Mo arrondi (2_500_000 bytes ≈ 2.38 Mo)
        big_entry = next(i for i in res["items"] if i["title"] == "Big file")
        self.assertAlmostEqual(big_entry["size"], round(2_500_000 / (1024 * 1024), 2))

    # ------------------------------
    # count_contents_types (operator != "and")
    # ------------------------------
    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_count_contents_types_operator_or_list(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search(
            {
                "type_of_request": "count_contents_types",
                "portal_type": ["Document", "Folder"],
                "operator": "or",
            }
        )
        items = {i["portal_type"]: i["nb_items"] for i in res["items"]}
        self.assertEqual(items, {"Document": 3, "Folder": 1})

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_count_contents_types_operator_or_single_type(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search(
            {
                "type_of_request": "count_contents_types",
                "portal_type": "Document",
                "operator": "or",
            }
        )
        self.assertEqual(res["items"], [{"portal_type": "Document", "nb_items": 3}])

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_count_contents_types_operator_or_no_type(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search(
            {"type_of_request": "count_contents_types", "operator": "or"}
        )
        self.assertEqual(res, {"items": []})

    # ------------------------------
    # check_value_of_field (edge cases)
    # ------------------------------
    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_check_value_of_field_empty_when_no_content(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search(
            {
                "type_of_request": "check_value_of_field",
                "portal_type": "NonExistentType",
                "field_name": "title",
                "expected_values": ["x"],
            }
        )
        self.assertEqual(res, {})

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_check_value_of_field_uses_catalog_metadata(self, mjson):
        # "Title" is a catalog metadata column: the fast path reads it from the
        # brain without waking up the object.
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search(
            {
                "type_of_request": "check_value_of_field",
                "portal_type": "Document",
                "field_name": "Title",
                "expected_values": ["Doc 1", "Doc 2"],
            }
        )
        self.assertEqual(res["Doc 1"]["count"], 1)
        self.assertEqual(res["Doc 2"]["count"], 1)

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_check_value_of_field_handles_list_values(self, mjson):
        # "subject" is not a catalog column, so the object is woken up and its
        # (list) value is normalized: real values are extended, empty and
        # all-None lists each count as a single None.
        mjson.return_value = FAKE_TYPES
        self.doc1.subject = ("keyword1", "keyword2")  # -> extend
        self.doc2.subject = ()  # -> single None
        self.page.subject = ("", "None")  # -> all None -> single None
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search(
            {
                "type_of_request": "check_value_of_field",
                "portal_type": "Document",
                "field_name": "subject",
                "expected_values": ["keyword1", "keyword2", "None"],
            }
        )
        self.assertEqual(res["keyword1"]["count"], 1)
        self.assertEqual(res["keyword2"]["count"], 1)
        self.assertEqual(res["None"]["count"], 2)  # doc2 (empty) + page (all None)

    # ------------------------------
    # normalize_catalog_params
    # ------------------------------
    def test_normalize_catalog_params(self):
        handler = FindEndpointHandler(self.portal, self.request)
        params = {
            "portal_type": ["a", "b"],
            "effective": {"query": "2025-12-12", "range": "min"},
            "bad_date": {"query": "not a date", "range": "max"},
            "num": 5,
        }
        res = handler.normalize_catalog_params(params)
        self.assertIsInstance(res["effective"]["query"], DateTime)
        self.assertEqual(res["effective"]["range"], "min")
        # Unparseable date is left as a string
        self.assertEqual(res["bad_date"]["query"], "not a date")
        self.assertEqual(res["portal_type"], ["a", "b"])
        self.assertEqual(res["num"], 5)

    # ------------------------------
    # search_from_json ("catalog" request)
    # ------------------------------
    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_search_from_json_returns_selected_attributes(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        # "text" is None on the brain, so its value is read from the awoken
        # object; "modified" is a DateTime metadata column.
        json_query = {
            "portal_type": "Document",
            "modified": {"query": "2000-01-01T00:00:00", "range": "min"},
            "text": "",
        }
        res = handler.search(
            {"type_of_request": "catalog", "json_str_query": json.dumps(json_query)}
        )
        self.assertEqual(len(res), 3)
        for item in res:
            self.assertEqual(item["portal_type"], "Document")
            self.assertIn("Title", item)
            self.assertIn("text", item)  # brain value None -> read from object
            self.assertTrue(item["getPath"].startswith("/plone/"))  # callable resolved
            self.assertIsInstance(item["modified"], str)  # DateTime -> ISO8601

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_search_from_json_has_children_of_type(self, mjson):
        mjson.return_value = FAKE_TYPES
        empty_folder = api.content.create(
            container=self.portal, type="Folder", title="Empty folder"
        )
        handler = FindEndpointHandler(self.portal, self.request)
        json_query = {"portal_type": "Folder", "_has_children_of_type": "Document"}
        res = handler.search(
            {"type_of_request": "catalog", "json_str_query": json.dumps(json_query)}
        )
        paths = [i["getPath"] for i in res]
        self.assertIn(self.folder.absolute_url_path(), paths)
        self.assertNotIn(empty_folder.absolute_url_path(), paths)

    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_search_from_json_falls_back_to_querybuilder(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        json_query = {"query": "irrelevant"}
        with patch(
            "imio.smartweb.common.rest.endpoint.api.portal.get_tool"
        ) as get_tool, patch(
            "plone.app.querystring.querybuilder.QueryBuilder"
        ) as query_builder:
            get_tool.return_value = MagicMock(side_effect=Exception("boom"))
            query_builder.return_value.return_value = []
            res = handler.search(
                {"type_of_request": "catalog", "json_str_query": json.dumps(json_query)}
            )
        self.assertEqual(res, [])
        query_builder.assert_called_once()

    # ------------------------------
    # Fallback to plone.restapi default search
    # ------------------------------
    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_unknown_request_falls_back_to_default_search(self, mjson):
        mjson.return_value = FAKE_TYPES
        handler = FindEndpointHandler(self.portal, self.request)
        res = handler.search({"type_of_request": "something_unknown"})
        self.assertIn("items", res)

    # ------------------------------
    # FindEndpoint service
    # ------------------------------
    @patch("imio.smartweb.common.rest.endpoint.get_json")
    def test_find_endpoint_reply(self, mjson):
        mjson.return_value = FAKE_TYPES
        self.request.form = {"type_of_request": "get_max_depth"}
        # plone.rest Service has no arg-taking __init__; the publisher sets
        # context/request as attributes.
        service = FindEndpoint()
        service.context = self.portal
        service.request = self.request
        res = service.reply()
        self.assertIn("max_depth", res)

    # ------------------------------
    # normalize_query_param helper
    # ------------------------------
    def test_normalize_query_param(self):
        self.assertEqual(normalize_query_param(["a", "b"]), ["a", "b"])
        self.assertEqual(normalize_query_param('["a", "b"]'), ["a", "b"])
        # Looks like a list but is invalid JSON -> wrapped as-is
        self.assertEqual(normalize_query_param("[bad json]"), ["[bad json]"])
        # Not bracketed -> wrapped as-is
        self.assertEqual(normalize_query_param("hello"), ["hello"])
        # Non str/list -> wrapped
        self.assertEqual(normalize_query_param(123), [123])


# <audit>
#   <file>test_rest_endpoint.py</file>
#   <requirements_applied>R1, R2, R5, R6</requirements_applied>
#   <deviations>
#     Extended the existing test file rather than creating a new one (R5/R6:
#     this is the single test file for endpoint.py). Real Plone content and
#     catalog are used throughout (R1); only the external @types HTTP call
#     (get_json) is mocked, matching the pre-existing tests. The QueryBuilder
#     fallback test additionally mocks the catalog tool to force the except
#     branch, and normalize_query_param (a module-level function) is tested as a
#     method on the existing TestRestEndpoint class to stay consistent with the
#     file's single-class layout.
#   </deviations>
#   <questions>None</questions>
# </audit>
