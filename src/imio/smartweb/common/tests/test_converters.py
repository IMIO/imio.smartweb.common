# -*- coding: utf-8 -*-

from imio.smartweb.common.converters import AjaxSelectChoiceDataConverter
from unittest.mock import MagicMock
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import unittest


class TestAjaxSelectChoiceDataConverter(unittest.TestCase):
    """z3c.form's fallback converter resolves a Choice token against the
    UNBOUND field, whose context-aware vocabulary is always empty. This
    converter resolves it against the widget's own vocabulary instead."""

    def setUp(self):
        self.vocabulary = SimpleVocabulary(
            [SimpleTerm(value="uid-1", token="uid-1", title="Amay » Bibliothèque")]
        )
        self.field = Choice(title="Contact", values=["uid-1"], required=False)
        self.widget = MagicMock()
        self.widget.get_vocabulary.return_value = self.vocabulary
        self.converter = AjaxSelectChoiceDataConverter(self.field, self.widget)

    def test_a_known_token_resolves_to_its_value(self):
        self.assertEqual(self.converter.toFieldValue("uid-1"), "uid-1")

    def test_the_widget_is_updated_before_reading_its_vocabulary(self):
        # get_vocabulary() is only populated once the widget has been updated.
        self.converter.toFieldValue("uid-1")
        self.widget.update.assert_called_once_with()

    def test_an_empty_value_becomes_the_missing_value(self):
        self.assertIs(self.converter.toFieldValue(""), self.field.missing_value)

    def test_an_unknown_token_is_handed_over_untouched(self):
        # z3c.form validates right after with the field bound to the real
        # content, which is where an out-of-scope contact is refused.
        self.assertEqual(self.converter.toFieldValue("uid-unknown"), "uid-unknown")

    def test_a_widget_without_vocabulary_hands_the_token_over(self):
        self.widget.get_vocabulary.return_value = None
        self.assertEqual(self.converter.toFieldValue("uid-1"), "uid-1")
