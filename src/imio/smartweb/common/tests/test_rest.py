# -*- coding: utf-8 -*-

from imio.smartweb.common.rest.odwb import OdwbService
from imio.smartweb.common.rest.utils import get_restapi_query_lang
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from unittest.mock import patch

import transaction
import unittest


class TestREST(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})

        self.doc1 = api.content.create(
            container=self.portal,
            type="Document",
            title="Doc 1",
        )
        self.doc1.topics = ["agriculture"]
        self.doc1.local_category = "Titre FR"
        self.doc1.local_category_nl = "NL title"
        self.doc1.local_category_de = "DE title"
        self.doc1.local_category_en = "EN title"
        api.content.transition(self.doc1, "publish")

        self.doc2 = api.content.create(
            container=self.portal,
            type="Document",
            title="Doc 2",
        )
        self.doc2.iam = ["young", "job_seeker"]
        self.doc2.topics = ["agriculture", "entertainment"]
        api.content.transition(self.doc2, "publish")

        self.event = api.content.create(
            container=self.portal,
            type="Event",
            title="Event",
        )
        api.content.transition(self.event, "publish")

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_restapi_query_lang(self):
        self.assertEqual(get_restapi_query_lang(), "fr")
        self.request.form["translated_in_nl"] = True
        self.assertEqual(get_restapi_query_lang(), "nl")
        self.request.form["translated_in_en"] = True
        self.assertEqual(get_restapi_query_lang(), "fr")

    def test_search_filters(self):
        query = {
            "portal_type": "Document",
            "metadata_fields": "not_existing",
        }
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertEqual(len(json), 1)

        query = {
            "portal_type": "Document",
            "metadata_fields": "topics",
        }
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertEqual(len(json), 1)

        query = {
            "portal_type": "Document",
            "metadata_fields": ["iam", "topics"],
        }
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertEqual(len(json), 2)
        self.assertEqual(
            json["iam"],
            [
                {"title": "Job seeker", "token": "job_seeker"},
                {"title": "Young", "token": "young"},
            ],
        )
        self.assertEqual(
            json["topics"],
            [
                {"title": "Agriculture", "token": "agriculture"},
                {"title": "Entertainment", "token": "entertainment"},
            ],
        )

        query = {
            "portal_type": "Document",
            "metadata_fields": "local_category",
        }
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertEqual(
            json["local_category"],
            [{"title": "Titre FR", "token": "Titre FR"}],
        )
        query["translated_in_nl"] = 1
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertEqual(
            json["local_category"],
            [{"title": "NL title", "token": "Titre FR"}],
        )
        del query["translated_in_nl"]

        query = {
            "portal_type": "Event",
            "metadata_fields": [
                "iam",
                "topics",
                "container_uid",
                "effective",
                "end",
                "has_leadimage",
                "start",
                "UID",
            ],
        }
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertNotIn("container_uid", json)
        self.assertNotIn("effective", json)
        self.assertNotIn("end", json)
        self.assertNotIn("has_leadimage", json)
        self.assertNotIn("start", json)
        self.assertNotIn("UID", json)

    @patch("imio.smartweb.common.utils.api.portal.get")
    def test_odwb_service_environnement(self, mock_get):
        mock_portal = mock_get.return_value
        mock_portal.absolute_url.return_value = "http://localhost:8080"
        endpoint = OdwbService()
        self.assertEqual(endpoint.available(), False)

        mock_portal.absolute_url.return_value = "https://www.production.be"
        endpoint = OdwbService()
        self.assertEqual(endpoint.available(), True)
