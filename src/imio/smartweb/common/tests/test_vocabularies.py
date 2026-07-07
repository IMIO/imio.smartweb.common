# -*- coding: utf-8 -*-

from imio.smartweb.common.config import DIRECTORY_URL
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase
from imio.smartweb.common.vocabularies import RemoteDirectoryEntitiesVocabulary
from unittest.mock import patch
from zope.schema.vocabulary import SimpleVocabulary


class TestVocabularies(ImioSmartwebCommonTestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_topics(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Topics", 17)

    def test_topics_de(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Topics_de", 17)

    def test_iam(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.IAm", 10)

    def test_iam_de(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.IAm_de", 10)

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
