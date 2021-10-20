# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

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
            "portal_type": "Event",
            "metadata_fields": [
                "iam",
                "topics",
                "effective",
                "end",
                "has_leadimage",
                "start",
                "UID",
            ],
        }
        response = self.api_session.get("/@search-filters", params=query)
        json = response.json()
        self.assertNotIn("effective", json)
        self.assertNotIn("end", json)
        self.assertNotIn("has_leadimage", json)
        self.assertNotIn("start", json)
        self.assertNotIn("UID", json)
