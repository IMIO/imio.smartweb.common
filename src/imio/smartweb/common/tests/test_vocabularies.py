# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase


class TestVocabularies(ImioSmartwebCommonTestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_topics(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Topics", 17)

    def test_iam(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.IAm", 10)

    def test_countries(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Countries", 240)

    def test_cities(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Cities", 898)

    def test_scales(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Scales", 3)
