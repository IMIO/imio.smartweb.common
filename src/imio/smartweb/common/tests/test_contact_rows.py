# -*- coding: utf-8 -*-

from imio.smartweb.common.contact.rows import IContactInformationsGrids
from imio.smartweb.common.contact.rows import IMailDisplayRow
from imio.smartweb.common.contact.rows import IPhoneDisplayRow
from imio.smartweb.common.contact.rows import IUrlDisplayRow
from plone.autoform.interfaces import MODES_KEY
from plone.autoform.interfaces import WIDGETS_KEY
from plone.supermodel import model
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.utils import mergedTaggedValueDict
from plone.supermodel.utils import mergedTaggedValueList
from zope import schema

import unittest


class IDerived(IContactInformationsGrids):
    """A schema inheriting the shared grids, like the real consumers do.

    ISectionContact (imio.smartweb.core) and ISecondaryContact
    (imio.events.core) both inherit IContactInformationsGrids exactly this way.
    """

    extra = schema.TextLine(title="Extra", required=False)


class TestGridsMixinInheritance(unittest.TestCase):
    """The guard on the assumption IContactInformationsGrids rests on.

    plone.autoform and plone.supermodel must collect fieldsets, widget
    directives and mode directives from an interface's BASES, not only from the
    interface itself. If these tests ever fail, the mixin cannot work and the
    fallback is to declare the three grid fields in each product.
    """

    def test_derived_schema_inherits_the_grid_fields(self):
        names = schema.getFieldNamesInOrder(IDerived)
        self.assertIn("phones_display", names)
        self.assertIn("mails_display", names)
        self.assertIn("urls_display", names)
        self.assertIn("extra", names)

    def test_derived_schema_inherits_the_fieldset(self):
        fieldsets = mergedTaggedValueList(IDerived, FIELDSETS_KEY)
        names = [fieldset.__name__ for fieldset in fieldsets]
        self.assertIn("contact_informations", names)
        fieldset = [f for f in fieldsets if f.__name__ == "contact_informations"][0]
        self.assertEqual(
            ["phones_display", "mails_display", "urls_display"],
            list(fieldset.fields),
        )

    def test_derived_schema_inherits_the_widget_directives(self):
        widgets = mergedTaggedValueDict(IDerived, WIDGETS_KEY)
        self.assertIn("phones_display", widgets)
        self.assertIn("mails_display", widgets)
        self.assertIn("urls_display", widgets)

    def test_grids_mixin_is_a_model_schema(self):
        self.assertTrue(issubclass(IContactInformationsGrids, model.Schema))


class TestRowSchemasAreFlat(unittest.TestCase):
    """Row schemas must declare every column themselves, never inherit one.

    collective.z3cform.datagridfield's DictRowConverter.toFieldValue iterates
    `self.field.schema.namesAndDescriptions()` WITHOUT `all=True`, so it only
    sees an interface's OWN attributes. A column inherited from a base
    interface is silently dropped from the converted row and comes back out of
    storage with its key missing -- which shows up far away, as a KeyError when
    reading the saved value, not as a form error.

    This is the regression guard for exactly that: an attempt to factor the
    three identity columns into a shared base broke the section's save
    round-trip with `KeyError: 'contact_uid'`.
    """

    ROW_SCHEMAS = (IPhoneDisplayRow, IMailDisplayRow, IUrlDisplayRow)

    def test_no_column_is_inherited(self):
        for row_schema in self.ROW_SCHEMAS:
            own = {name for name, _ in row_schema.namesAndDescriptions()}
            self.assertEqual(
                set(schema.getFieldNamesInOrder(row_schema)),
                own,
                "{}: some columns are inherited and datagridfield would drop "
                "them".format(row_schema.__name__),
            )

    def test_the_identity_columns_are_declared_on_each_row_schema(self):
        for row_schema in self.ROW_SCHEMAS:
            own = {name for name, _ in row_schema.namesAndDescriptions()}
            for column in ("contact_uid", "type_token", "contact_title"):
                self.assertIn(column, own, row_schema.__name__)


class TestRowSchemas(unittest.TestCase):
    ROW_SCHEMAS = (IPhoneDisplayRow, IMailDisplayRow, IUrlDisplayRow)

    def test_every_row_schema_carries_the_common_columns(self):
        for row_schema in self.ROW_SCHEMAS:
            names = schema.getFieldNamesInOrder(row_schema)
            self.assertIn("contact_uid", names, row_schema.__name__)
            self.assertIn("type_token", names, row_schema.__name__)
            self.assertIn("contact_title", names, row_schema.__name__)
            self.assertIn("visible_columns", names, row_schema.__name__)

    def test_the_identity_columns_are_hidden_in_every_row_schema(self):
        # Declared once on the shared base; each row schema must inherit them.
        for row_schema in self.ROW_SCHEMAS:
            modes = mergedTaggedValueList(row_schema, MODES_KEY)
            hidden = [name for _, name, mode in modes if mode == "hidden"]
            self.assertIn("contact_uid", hidden, row_schema.__name__)
            self.assertIn("type_token", hidden, row_schema.__name__)

    def test_the_data_columns_use_the_frozen_label_widget(self):
        expected = {
            IPhoneDisplayRow: ("contact_title", "label", "type", "number"),
            IMailDisplayRow: ("contact_title", "label", "type", "mail_address"),
            IUrlDisplayRow: ("contact_title", "type", "url"),
        }
        for row_schema, columns in expected.items():
            widgets = mergedTaggedValueDict(row_schema, WIDGETS_KEY)
            for column in columns:
                self.assertIn(
                    column, widgets, "{}.{}".format(row_schema.__name__, column)
                )

    def test_phone_row_columns(self):
        names = schema.getFieldNamesInOrder(IPhoneDisplayRow)
        for column in ("label", "type", "number"):
            self.assertIn(column, names)

    def test_mail_row_columns(self):
        names = schema.getFieldNamesInOrder(IMailDisplayRow)
        for column in ("label", "type", "mail_address"):
            self.assertIn(column, names)

    def test_url_row_columns(self):
        names = schema.getFieldNamesInOrder(IUrlDisplayRow)
        for column in ("type", "url"):
            self.assertIn(column, names)

    def test_url_row_has_no_label_column(self):
        # The directory's url rows carry no label; the vocabulary must match.
        self.assertNotIn("label", schema.getFieldNamesInOrder(IUrlDisplayRow))

    def test_visible_columns_is_optional_so_a_row_can_be_saved_untouched(self):
        for row_schema in self.ROW_SCHEMAS:
            self.assertFalse(
                row_schema["visible_columns"].required, row_schema.__name__
            )
