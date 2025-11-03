# -*- coding: utf-8 -*-
from imio.smartweb.common.rest.endpoint import FindEndpointHandler
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile, NamedBlobImage
from unittest.mock import patch
from zExceptions import Unauthorized

import unittest


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
