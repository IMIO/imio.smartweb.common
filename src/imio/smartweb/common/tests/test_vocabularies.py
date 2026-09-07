# -*- coding: utf-8 -*-

from imio.smartweb.common.config import DIRECTORY_URL
from imio.smartweb.common.interfaces import ILocalManagerAware
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase
from imio.smartweb.common.vocabularies import DIRECTORY_ENTITIES_CACHE_TTL
from imio.smartweb.common.vocabularies import RemoteDirectoryContactVocabulary
from imio.smartweb.common.vocabularies import RemoteDirectoryEntitiesVocabulary
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest.mock import MagicMock
from unittest.mock import patch
from urllib.parse import parse_qs
from urllib.parse import urlparse
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json
import unittest


class TestVocabularies(ImioSmartwebCommonTestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        # The factory is a module-level singleton and its cache is a dict held
        # on the class, so it would otherwise leak from one test to the next.
        # Every remote-directory test below relies on this, including the two
        # asserting `assert_called_once_with`.
        RemoteDirectoryEntitiesVocabulary._cache.clear()

    def test_topics(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Topics", 17)

    def test_topics_de(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Topics_de", 17)

    def test_iam(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.IAm", 10)

    def test_iam_de(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.IAm_de", 10)

    def test_topics_de_is_memoized(self):
        factory = getUtility(IVocabularyFactory, "imio.smartweb.vocabulary.Topics_de")
        self.assertIs(factory(), factory())

    def test_iam_de_is_memoized(self):
        factory = getUtility(IVocabularyFactory, "imio.smartweb.vocabulary.IAm_de")
        self.assertIs(factory(), factory())

    def test_countries(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Countries", 240)

    def test_cities(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Cities", 898)

    def test_scales(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Scales", 3)

    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_remote_directory_entities_uses_registry_url(self, mock_get_voc):
        expected = SimpleVocabulary([])
        mock_get_voc.return_value = expected
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            result = RemoteDirectoryEntitiesVocabulary()
        self.assertIs(result, expected)
        mock_get_voc.assert_called_once_with(
            "imio.directory.Entity", "http://dir.example"
        )

    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_remote_directory_entities_falls_back_to_default_url(self, mock_get_voc):
        # Empty registry record -> the module DIRECTORY_URL default is used.
        expected = SimpleVocabulary([])
        mock_get_voc.return_value = expected
        with patch("plone.api.portal.get_registry_record", return_value=""):
            RemoteDirectoryEntitiesVocabulary()
        mock_get_voc.assert_called_once_with("imio.directory.Entity", DIRECTORY_URL)

    @patch("imio.smartweb.common.vocabularies.time")
    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_remote_directory_entities_are_cached(self, mock_get_voc, mock_time):
        # Time is frozen rather than read from the wall clock, so the cache-hit
        # path cannot be defeated by a deadline falling between the two calls.
        mock_time.return_value = 1000.0
        mock_get_voc.return_value = SimpleVocabulary(
            [SimpleTerm(value="uid1", token="uid1", title="Entity 1")]
        )
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            first = RemoteDirectoryEntitiesVocabulary()
            second = RemoteDirectoryEntitiesVocabulary()
        self.assertIs(first, second)
        self.assertEqual(mock_get_voc.call_count, 1)

    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_empty_remote_directory_entities_are_not_cached(self, mock_get_voc):
        # An empty vocabulary means the remote call failed: caching it would
        # freeze an empty entity list in every form for the whole TTL.
        mock_get_voc.return_value = SimpleVocabulary([])
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            RemoteDirectoryEntitiesVocabulary()
            RemoteDirectoryEntitiesVocabulary()
        self.assertEqual(mock_get_voc.call_count, 2)

    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_remote_directory_entities_cache_is_keyed_on_url(self, mock_get_voc):
        mock_get_voc.return_value = SimpleVocabulary(
            [SimpleTerm(value="uid1", token="uid1", title="Entity 1")]
        )
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            RemoteDirectoryEntitiesVocabulary()
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://other.example"
        ):
            RemoteDirectoryEntitiesVocabulary()
        self.assertEqual(mock_get_voc.call_count, 2)
        self.assertEqual(
            mock_get_voc.call_args_list[-1][0],
            ("imio.directory.Entity", "http://other.example"),
        )

    @patch("imio.smartweb.common.vocabularies.time")
    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_remote_directory_entities_cache_is_keyed_on_language(
        self, mock_get_voc, mock_time
    ):
        # get_json negotiates the current language into the remote @search
        # (utils.py:41-43), so the same url under another language is another
        # response and must not be served from the first language's entry.
        mock_time.return_value = 1000.0
        fr_vocabulary = SimpleVocabulary(
            [SimpleTerm(value="uid1", token="uid1", title="Entité")]
        )
        de_vocabulary = SimpleVocabulary(
            [SimpleTerm(value="uid1", token="uid1", title="Einheit")]
        )
        mock_get_voc.side_effect = [fr_vocabulary, de_vocabulary]
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            with patch(
                "imio.smartweb.common.vocabularies.api.portal.get_current_language",
                return_value="fr",
            ):
                first = RemoteDirectoryEntitiesVocabulary()
            with patch(
                "imio.smartweb.common.vocabularies.api.portal.get_current_language",
                return_value="de",
            ):
                second = RemoteDirectoryEntitiesVocabulary()
        self.assertEqual(mock_get_voc.call_count, 2)
        self.assertIs(first, fr_vocabulary)
        self.assertIs(second, de_vocabulary)
        # The cache is a dict, not a single slot: caching "de" must not evict
        # "fr", otherwise alternating traffic would never hit the cache.
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            with patch(
                "imio.smartweb.common.vocabularies.api.portal.get_current_language",
                return_value="fr",
            ):
                third = RemoteDirectoryEntitiesVocabulary()
        self.assertEqual(mock_get_voc.call_count, 2)
        self.assertIs(third, fr_vocabulary)

    @patch("imio.smartweb.common.vocabularies.time")
    @patch("imio.smartweb.common.vocabularies.get_entities_vocabulary")
    def test_remote_directory_entities_cache_expires(self, mock_get_voc, mock_time):
        # Both halves of the TTL contract, so that the test cannot pass with no
        # cache at all: the entry must still be served one second before its
        # deadline (the full 300s, not a fraction of it), and must be refetched
        # once the deadline is reached.
        expected = SimpleVocabulary(
            [SimpleTerm(value="uid1", token="uid1", title="Entity 1")]
        )
        mock_get_voc.return_value = expected
        with patch(
            "plone.api.portal.get_registry_record", return_value="http://dir.example"
        ):
            mock_time.return_value = 1000.0
            first = RemoteDirectoryEntitiesVocabulary()
            mock_time.return_value = 1000.0 + DIRECTORY_ENTITIES_CACHE_TTL - 1
            second = RemoteDirectoryEntitiesVocabulary()
            self.assertEqual(mock_get_voc.call_count, 1)
            self.assertIs(second, first)
            mock_time.return_value = 1000.0 + DIRECTORY_ENTITIES_CACHE_TTL
            RemoteDirectoryEntitiesVocabulary()
        self.assertEqual(mock_get_voc.call_count, 2)


REQUESTS_GET = "imio.smartweb.common.utils.requests.get"

LINKED_ENTITY_UID = "11111111111111111111111111111111"
CONTACT_UID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def fake_directory_search(url, headers=None, timeout=None):
    """Answer a directory ``@search`` the way the real one does.

    Honours the three criteria the vocabulary builds: ``selected_entities``
    (scope), ``SearchableText`` (search) and ``UID`` (single term lookup).
    """
    query = parse_qs(urlparse(url).query)
    entities = query.get("selected_entities")
    searchable = query.get("SearchableText")
    uids = query.get("UID")
    items = []
    if entities is None or LINKED_ENTITY_UID in entities:
        items = [{"UID": CONTACT_UID, "breadcrumb": "Amay » Bibliothèque"}]
    if searchable and not searchable[0].startswith("Bib"):
        items = []
    if uids is not None and CONTACT_UID not in uids:
        items = []
    response = MagicMock()
    response.status_code = 200
    response.text = json.dumps({"items": items, "items_total": len(items)})
    return response


class TestRemoteDirectoryContactVocabulary(unittest.TestCase):
    """The vocabulary resolves its scope from the nearest ILocalManagerAware
    ancestor, which is the Entity in every consuming package."""

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal, type="Folder", id="entity", title="Entity"
        )
        alsoProvides(self.entity, ILocalManagerAware)
        self.entity.directory_linked_entities = [LINKED_ENTITY_UID]
        self.child = api.content.create(
            container=self.entity, type="Folder", id="child", title="Child"
        )

    def test_no_entity_ancestor_gives_an_empty_vocabulary(self):
        vocabulary = RemoteDirectoryContactVocabulary(self.portal)
        self.assertEqual(len(vocabulary), 0)

    def test_entity_without_linked_entities_gives_an_empty_vocabulary(self):
        self.entity.directory_linked_entities = []
        vocabulary = RemoteDirectoryContactVocabulary(self.child)
        self.assertEqual(len(vocabulary), 0)

    def test_entity_without_the_field_at_all_gives_an_empty_vocabulary(self):
        # A package using imio.smartweb.common may have an Entity that never
        # got the field: degrade to empty rather than raise.
        del self.entity.directory_linked_entities
        vocabulary = RemoteDirectoryContactVocabulary(self.child)
        self.assertEqual(len(vocabulary), 0)

    def test_scope_is_resolved_from_a_nested_context(self):
        with patch(REQUESTS_GET, side_effect=fake_directory_search):
            vocabulary = RemoteDirectoryContactVocabulary(self.child)
            terms = list(vocabulary)
        self.assertEqual([term.value for term in terms], [CONTACT_UID])

    def test_term_title_is_the_breadcrumb(self):
        with patch(REQUESTS_GET, side_effect=fake_directory_search):
            term = RemoteDirectoryContactVocabulary(self.child).getTerm(CONTACT_UID)
        self.assertEqual(term.title, "Amay » Bibliothèque")

    def test_search_turns_each_word_into_a_prefix(self):
        with patch(REQUESTS_GET, side_effect=fake_directory_search) as mock_get:
            RemoteDirectoryContactVocabulary(self.child).search("Bib libr")
        query = parse_qs(urlparse(mock_get.call_args[0][0]).query)
        self.assertEqual(query["SearchableText"], ["Bib* AND libr*"])

    def test_search_is_scoped_to_the_linked_entities(self):
        with patch(REQUESTS_GET, side_effect=fake_directory_search) as mock_get:
            RemoteDirectoryContactVocabulary(self.child).search("Bib")
        query = parse_qs(urlparse(mock_get.call_args[0][0]).query)
        self.assertEqual(query["selected_entities"], [LINKED_ENTITY_UID])
        self.assertEqual(query["portal_type"], ["imio.directory.Contact"])
        self.assertEqual(query["b_size"], ["20"])

    def test_search_honours_the_registry_overridden_directory_url(self):
        # imio.smartweb.common.directory_url (registry.xml) lets a site (e.g.
        # staging) point at another directory than the DIRECTORY_URL default;
        # get_directory_url() is what RemoteDirectoryEntitiesVocabulary already
        # relies on for that, and _fetch() must go through the same helper so
        # the two vocabularies never end up querying different directories.
        # Relying on the integration layer's per-test transaction abort to
        # restore the record, like every other test in this module relies on
        # it to restore content.
        api.portal.set_registry_record(
            "imio.smartweb.common.directory_url", "https://annuaire.example.test"
        )
        with patch(REQUESTS_GET, side_effect=fake_directory_search) as mock_get:
            RemoteDirectoryContactVocabulary(self.child).search("Bib")
        self.assertEqual(
            urlparse(mock_get.call_args[0][0]).netloc, "annuaire.example.test"
        )

    def test_an_unknown_token_raises_lookup_error(self):
        with patch(REQUESTS_GET, side_effect=fake_directory_search):
            vocabulary = RemoteDirectoryContactVocabulary(self.child)
            with self.assertRaises(LookupError):
                vocabulary.getTermByToken("does-not-exist")

    def test_contains_answers_from_the_directory(self):
        with patch(REQUESTS_GET, side_effect=fake_directory_search):
            vocabulary = RemoteDirectoryContactVocabulary(self.child)
            self.assertIn(CONTACT_UID, vocabulary)
            self.assertNotIn("does-not-exist", vocabulary)
