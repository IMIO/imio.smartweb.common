# -*- coding: utf-8 -*-

from imio.smartweb.common.config import DIRECTORY_URL
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase
from imio.smartweb.common.vocabularies import DIRECTORY_ENTITIES_CACHE_TTL
from imio.smartweb.common.vocabularies import RemoteDirectoryEntitiesVocabulary
from unittest.mock import patch
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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
