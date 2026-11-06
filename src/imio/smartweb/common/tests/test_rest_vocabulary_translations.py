# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

import unittest


class TestVocabularyTranslations(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})

    def tearDown(self):
        self.api_session.close()

    def test_vocabulary_titles_in_all_languages(self):
        response = self.api_session.get(
            "@vocabulary-translations/imio.smartweb.vocabulary.IAm"
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertEqual(
            json["@id"],
            f"{self.portal_url}/@vocabulary-translations/imio.smartweb.vocabulary.IAm",
        )
        self.assertEqual(json["items_total"], 10)
        self.assertEqual(
            json["items"][0],
            {
                "token": "merchant",
                "fr": "Commerçant",
                "nl": "Handelaar",
                "de": "Händler",
                "en": "Merchant",
            },
        )

    def test_unknown_vocabulary(self):
        response = self.api_session.get("@vocabulary-translations/unknown")
        self.assertEqual(response.status_code, 404)

    def test_missing_vocabulary_name(self):
        response = self.api_session.get("@vocabulary-translations")
        self.assertEqual(response.status_code, 400)

    def test_protected_vocabulary(self):
        response = self.api_session.get(
            "@vocabulary-translations/plone.app.vocabularies.Users"
        )
        self.assertEqual(response.status_code, 401)
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        response = self.api_session.get(
            "@vocabulary-translations/plone.app.vocabularies.Users"
        )
        self.assertEqual(response.status_code, 200)
