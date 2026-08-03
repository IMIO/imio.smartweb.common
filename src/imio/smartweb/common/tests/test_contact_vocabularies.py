# -*- coding: utf-8 -*-

from imio.smartweb.common.contact.rows import IMailDisplayRow
from imio.smartweb.common.contact.rows import IPhoneDisplayRow
from imio.smartweb.common.contact.rows import IUrlDisplayRow
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from zope import schema
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestContactDisplayColumnsVocabularies(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def _tokens(self, name):
        factory = getUtility(IVocabularyFactory, name)
        return [term.token for term in factory()]

    def test_phone_display_columns(self):
        self.assertEqual(
            ["label", "type", "number"],
            self._tokens("imio.smartweb.vocabulary.PhoneDisplayColumns"),
        )

    def test_mail_display_columns(self):
        self.assertEqual(
            ["label", "type", "mail_address"],
            self._tokens("imio.smartweb.vocabulary.MailDisplayColumns"),
        )

    def test_url_display_columns(self):
        self.assertEqual(
            ["type", "url"],
            self._tokens("imio.smartweb.vocabulary.UrlDisplayColumns"),
        )

    def test_terms_have_a_human_title(self):
        factory = getUtility(
            IVocabularyFactory, "imio.smartweb.vocabulary.PhoneDisplayColumns"
        )
        titles = {term.token: term.title for term in factory()}
        # The title is a translatable msgid, not the raw token.
        self.assertNotEqual("number", titles["number"])
        self.assertTrue(titles["number"])

    def test_a_row_schema_can_resolve_its_own_vocabulary(self):
        # The rows declare their vocabulary by NAME; if the utility were
        # missing or misnamed the field would blow up only at render time.
        expected = {
            IPhoneDisplayRow: ["label", "type", "number"],
            IMailDisplayRow: ["label", "type", "mail_address"],
            IUrlDisplayRow: ["type", "url"],
        }
        for row_schema, columns in expected.items():
            value_type = row_schema["visible_columns"].value_type
            vocabulary = getUtility(IVocabularyFactory, value_type.vocabularyName)()
            self.assertEqual(
                columns,
                [term.token for term in vocabulary],
                row_schema.__name__,
            )


class TestVocabulariesMirrorTheRowSchemas(unittest.TestCase):
    """The vocabularies and the row data columns must not drift apart.

    A token in the vocabulary with no matching field on the row would let an
    editor tick a column that can never be rendered, and a data field missing
    from the vocabulary could never be hidden.
    """

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    NON_DATA_COLUMNS = {"contact_uid", "type_token", "contact_title", "visible_columns"}

    def test_every_vocabulary_token_is_a_field_of_its_row_schema(self):
        pairs = (
            (IPhoneDisplayRow, "imio.smartweb.vocabulary.PhoneDisplayColumns"),
            (IMailDisplayRow, "imio.smartweb.vocabulary.MailDisplayColumns"),
            (IUrlDisplayRow, "imio.smartweb.vocabulary.UrlDisplayColumns"),
        )
        for row_schema, vocabulary_name in pairs:
            names = set(schema.getFieldNamesInOrder(row_schema))
            tokens = {
                term.token for term in getUtility(IVocabularyFactory, vocabulary_name)()
            }
            self.assertEqual(
                set(),
                tokens - names,
                "{}: vocabulary tokens absent from the schema".format(
                    row_schema.__name__
                ),
            )
            self.assertEqual(
                set(),
                (names - self.NON_DATA_COLUMNS) - tokens,
                "{}: data columns absent from the vocabulary".format(
                    row_schema.__name__
                ),
            )
