# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from imio.smartweb.common.widgets.select import TranslatedAjaxSelectWidget
from plone.api import portal as portal_api
from zope.publisher.browser import TestRequest

import mock
import unittest


class TestVocabulary(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = TestRequest()

    def test_translated_ajax_select(self):
        portal_api.get_current_language = mock.Mock(return_value="fr")
        widget = TranslatedAjaxSelectWidget(self.request)
        widget.update()
        self.assertEqual(
            {
                "name": None,
                "value": "",
                "pattern": "select2",
                "pattern_options": {"separator": ";"},
            },
            widget._base_args(),
        )

        widget.vocabulary = "imio.smartweb.vocabulary.Topics"
        self.assertEqual(
            widget._base_args(),
            {
                "name": None,
                "value": "",
                "pattern": "select2",
                "pattern_options": {
                    "vocabularyUrl": "http://nohost/plone/@@getVocabulary?name=imio.smartweb.vocabulary.Topics",
                    "separator": ";",
                },
            },
        )
        widget.value = "entertainment"
        self.assertEqual(
            widget._base_args(),
            {
                "name": None,
                "value": "entertainment",
                "pattern": "select2",
                "pattern_options": {
                    "vocabularyUrl": "http://nohost/plone/@@getVocabulary?name=imio.smartweb.vocabulary.Topics",
                    "initialValues": {
                        "entertainment": "Activités et divertissement",
                    },
                    "separator": ";",
                },
            },
        )
