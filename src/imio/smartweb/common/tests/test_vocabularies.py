# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from imio.smartweb.common.testing import ImioSmartwebCommonTestCase


class TestVocabularies(ImioSmartwebCommonTestCase):

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_topics(self):
        self.assertVocabularyLen("imio.smartweb.vocabulary.Topics", 6)
