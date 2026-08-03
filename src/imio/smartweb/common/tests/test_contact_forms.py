# -*- coding: utf-8 -*-

from imio.smartweb.common.contact.forms import CONTACT_UIDS_SEPARATOR
from imio.smartweb.common.contact.forms import ContactInformationsGridMixin
from imio.smartweb.common.contact.forms import DISPLAY_FIELDS
from imio.smartweb.common.contact.forms import EXTRA_ROW_COLUMNS
from imio.smartweb.common.contact.forms import KIND_BY_FIELD

import unittest


class _Request:
    def __init__(self, form):
        self.form = form


class _Form(ContactInformationsGridMixin):
    """Just enough of a z3c.form to exercise the request-rewriting helpers.

    Those helpers only read and write `self.request.form` and `self.prefix`, so
    they need no content type and no Plone site. End-to-end form behaviour is
    covered by imio.smartweb.core's section-form tests and imio.events.core's
    Secondary contact tests.
    """

    prefix = "form."

    def __init__(self, form):
        self.request = _Request(form)


class TestMixinConstants(unittest.TestCase):
    def test_display_fields(self):
        self.assertEqual(
            ("phones_display", "mails_display", "urls_display"), DISPLAY_FIELDS
        )

    def test_kind_by_field(self):
        self.assertEqual(
            {
                "phones_display": "phones",
                "mails_display": "mails",
                "urls_display": "urls",
            },
            KIND_BY_FIELD,
        )

    def test_kind_by_field_covers_every_display_field(self):
        self.assertEqual(set(DISPLAY_FIELDS), set(KIND_BY_FIELD))

    def test_extra_row_columns(self):
        self.assertEqual(
            ("contact_uid", "contact_title", "type_token"), EXTRA_ROW_COLUMNS
        )

    def test_separator_is_the_ajax_widget_s_own(self):
        self.assertEqual(";", CONTACT_UIDS_SEPARATOR)

    def test_default_uids_field_is_the_multi_valued_one(self):
        self.assertEqual(
            "related_contacts", ContactInformationsGridMixin.contact_uids_field
        )

    def test_load_button_name_is_prefixed(self):
        self.assertEqual(
            "form.buttons.load_contact_informations", _Form({})._load_button_name
        )


class TestSubmittedContactUids(unittest.TestCase):
    def test_separator_joined_string_is_split(self):
        form = _Form(
            {"form.widgets.related_contacts": CONTACT_UIDS_SEPARATOR.join(["a", "b"])}
        )
        self.assertEqual(["a", "b"], form._submitted_contact_uids())

    def test_a_plain_single_value_is_accepted(self):
        form = _Form({"form.widgets.related_contacts": "a"})
        self.assertEqual(["a"], form._submitted_contact_uids())

    def test_a_list_is_accepted(self):
        form = _Form({"form.widgets.related_contacts": ["a", "b"]})
        self.assertEqual(["a", "b"], form._submitted_contact_uids())

    def test_blanks_are_dropped_and_values_stripped(self):
        form = _Form({"form.widgets.related_contacts": ["  a  ", "", None]})
        self.assertEqual(["a"], form._submitted_contact_uids())

    def test_nothing_submitted_gives_an_empty_list(self):
        self.assertEqual([], _Form({})._submitted_contact_uids())

    def test_an_empty_string_gives_an_empty_list(self):
        form = _Form({"form.widgets.related_contacts": ""})
        self.assertEqual([], form._submitted_contact_uids())

    def test_the_field_name_is_overridable(self):
        class _Single(_Form):
            contact_uids_field = "related_contact"

        form = _Single({"form.widgets.related_contact": "a"})
        self.assertEqual(["a"], form._submitted_contact_uids())

    def test_the_default_field_is_not_read_when_overridden(self):
        class _Single(_Form):
            contact_uids_field = "related_contact"

        form = _Single({"form.widgets.related_contacts": "wrong"})
        self.assertEqual([], form._submitted_contact_uids())


class TestExtractPreferences(unittest.TestCase):
    prefix = "form.widgets.phones_display"

    def test_checked_columns_are_read_back(self):
        form = _Form(
            {
                f"{self.prefix}.0.widgets.contact_uid": "uid-1",
                f"{self.prefix}.0.widgets.number": "081",
                f"{self.prefix}.0.widgets.visible_columns": ["number"],
            }
        )
        self.assertEqual(
            {("uid-1", "081"): ["number"]},
            form._extract_preferences(self.prefix, "phones"),
        )

    def test_nothing_submitted_for_a_rendered_row_means_all_unchecked(self):
        # The widget WAS rendered (contact_uid is present), so "no checkbox
        # submitted" can only mean "everything unchecked" -- an EMPTY list, not
        # a missing key.
        form = _Form(
            {
                f"{self.prefix}.0.widgets.contact_uid": "uid-1",
                f"{self.prefix}.0.widgets.number": "081",
            }
        )
        self.assertEqual(
            {("uid-1", "081"): []}, form._extract_preferences(self.prefix, "phones")
        )

    def test_a_single_checked_column_arrives_as_a_string(self):
        form = _Form(
            {
                f"{self.prefix}.0.widgets.contact_uid": "uid-1",
                f"{self.prefix}.0.widgets.number": "081",
                f"{self.prefix}.0.widgets.visible_columns": "number",
            }
        )
        self.assertEqual(
            {("uid-1", "081"): ["number"]},
            form._extract_preferences(self.prefix, "phones"),
        )

    def test_a_row_without_a_key_is_skipped(self):
        form = _Form(
            {
                f"{self.prefix}.0.widgets.contact_uid": "uid-1",
                f"{self.prefix}.0.widgets.number": "  ",
                f"{self.prefix}.0.widgets.visible_columns": ["number"],
            }
        )
        self.assertEqual({}, form._extract_preferences(self.prefix, "phones"))

    def test_several_rows_are_all_read(self):
        form = _Form(
            {
                f"{self.prefix}.0.widgets.contact_uid": "uid-1",
                f"{self.prefix}.0.widgets.number": "081",
                f"{self.prefix}.0.widgets.visible_columns": ["number"],
                f"{self.prefix}.1.widgets.contact_uid": "uid-1",
                f"{self.prefix}.1.widgets.number": "082",
                f"{self.prefix}.1.widgets.visible_columns": ["label", "number"],
            }
        )
        self.assertEqual(
            {("uid-1", "081"): ["number"], ("uid-1", "082"): ["label", "number"]},
            form._extract_preferences(self.prefix, "phones"),
        )

    def test_scanning_stops_at_the_first_missing_index(self):
        form = _Form(
            {
                f"{self.prefix}.0.widgets.contact_uid": "uid-1",
                f"{self.prefix}.0.widgets.number": "081",
                # index 1 absent on purpose
                f"{self.prefix}.2.widgets.contact_uid": "uid-1",
                f"{self.prefix}.2.widgets.number": "082",
            }
        )
        self.assertEqual(
            {("uid-1", "081"): []}, form._extract_preferences(self.prefix, "phones")
        )

    def test_the_key_column_depends_on_the_kind(self):
        prefix = "form.widgets.mails_display"
        form = _Form(
            {
                f"{prefix}.0.widgets.contact_uid": "uid-1",
                f"{prefix}.0.widgets.mail_address": "a@b.be",
                f"{prefix}.0.widgets.visible_columns": ["mail_address"],
            }
        )
        self.assertEqual(
            {("uid-1", "a@b.be"): ["mail_address"]},
            form._extract_preferences(prefix, "mails"),
        )

    def test_no_rows_gives_no_preferences(self):
        self.assertEqual({}, _Form({})._extract_preferences(self.prefix, "phones"))


class TestWriteGrid(unittest.TestCase):
    prefix = "form.widgets.phones_display"

    def _rows(self):
        return [
            {
                "contact_uid": "uid-1",
                "contact_title": "Service culture",
                "type_token": "work",
                "label": "Accueil",
                "type": "Telephone de travail",
                "number": "081",
                "visible_columns": ["number"],
            }
        ]

    def test_stale_keys_of_the_grid_are_cleared(self):
        form = _Form({f"{self.prefix}.9.widgets.number": "stale", "other": "kept"})
        form._write_grid(self.prefix, "phones", [])
        self.assertNotIn(f"{self.prefix}.9.widgets.number", form.request.form)
        self.assertEqual("kept", form.request.form["other"])

    def test_another_grid_is_not_cleared(self):
        other = "form.widgets.mails_display"
        form = _Form({f"{other}.0.widgets.mail_address": "a@b.be"})
        form._write_grid(self.prefix, "phones", [])
        self.assertEqual("a@b.be", form.request.form[f"{other}.0.widgets.mail_address"])

    def test_every_column_is_written_including_the_hidden_ones(self):
        form = _Form({})
        form._write_grid(self.prefix, "phones", self._rows())
        written = form.request.form
        row = f"{self.prefix}.0.widgets"
        self.assertEqual("uid-1", written[f"{row}.contact_uid"])
        self.assertEqual("Service culture", written[f"{row}.contact_title"])
        self.assertEqual("work", written[f"{row}.type_token"])
        self.assertEqual("Accueil", written[f"{row}.label"])
        self.assertEqual("Telephone de travail", written[f"{row}.type"])
        self.assertEqual("081", written[f"{row}.number"])

    def test_visible_columns_and_its_empty_marker_are_written(self):
        form = _Form({})
        form._write_grid(self.prefix, "phones", self._rows())
        row = f"{self.prefix}.0.widgets"
        self.assertEqual(["number"], form.request.form[f"{row}.visible_columns"])
        self.assertEqual("1", form.request.form[f"{row}.visible_columns-empty-marker"])

    def test_an_empty_visible_columns_still_writes_the_empty_marker(self):
        rows = self._rows()
        rows[0]["visible_columns"] = []
        form = _Form({})
        form._write_grid(self.prefix, "phones", rows)
        row = f"{self.prefix}.0.widgets"
        self.assertEqual([], form.request.form[f"{row}.visible_columns"])
        self.assertEqual("1", form.request.form[f"{row}.visible_columns-empty-marker"])

    def test_the_count_marker_matches_the_row_number(self):
        form = _Form({})
        form._write_grid(self.prefix, "phones", self._rows())
        self.assertEqual("1", form.request.form[f"{self.prefix}.count"])
        form._write_grid(self.prefix, "phones", [])
        self.assertEqual("0", form.request.form[f"{self.prefix}.count"])

    def test_a_missing_column_is_written_as_an_empty_string(self):
        rows = self._rows()
        del rows[0]["label"]
        form = _Form({})
        form._write_grid(self.prefix, "phones", rows)
        self.assertEqual("", form.request.form[f"{self.prefix}.0.widgets.label"])

    def test_urls_grid_writes_its_own_columns_only(self):
        prefix = "form.widgets.urls_display"
        rows = [
            {
                "contact_uid": "uid-1",
                "contact_title": "Service culture",
                "type_token": "website",
                "type": "Site web",
                "url": "https://ville.be",
                "visible_columns": ["url"],
            }
        ]
        form = _Form({})
        form._write_grid(prefix, "urls", rows)
        row = f"{prefix}.0.widgets"
        self.assertEqual("https://ville.be", form.request.form[f"{row}.url"])
        self.assertEqual("website", form.request.form[f"{row}.type_token"])
        # urls rows have no label column
        self.assertNotIn(f"{row}.label", form.request.form)

    def test_writing_is_idempotent(self):
        form = _Form({})
        form._write_grid(self.prefix, "phones", self._rows())
        first = dict(form.request.form)
        form._write_grid(self.prefix, "phones", self._rows())
        self.assertEqual(first, form.request.form)
