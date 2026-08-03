# -*- coding: utf-8 -*-

from imio.smartweb.common.contact.directory import build_display_rows
from imio.smartweb.common.contact.directory import CONTACT_ROW_COLUMNS
from imio.smartweb.common.contact.directory import CONTACT_ROW_KEYS
from imio.smartweb.common.contact.directory import displayed_rows
from imio.smartweb.common.contact.directory import get_remote_contacts
from imio.smartweb.common.contact.directory import row_key
from imio.smartweb.common.contact.directory import translated_type_label
from imio.smartweb.common.contact.directory import visible_columns_map
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest import mock

import unittest

CONTACT = {
    "UID": "uid-1",
    "title": "Service culture",
    "phones": [
        {"label": "Accueil", "type": "work", "number": "081 12 34 56"},
        {"label": "", "type": "cell", "number": "0470 00 00 00"},
        {"label": "Sans numero", "type": "work", "number": ""},
    ],
    "mails": [{"label": "", "type": "work", "mail_address": "culture@ville.be"}],
    "urls": [{"type": "website", "url": "https://ville.be"}],
}


class _Stored:
    """Minimal stand-in for a content object carrying the stored grids."""

    def __init__(self, **grids):
        for name, rows in grids.items():
            setattr(self, name, rows)


class TestRowIdentity(unittest.TestCase):
    def test_key_column_of_each_kind(self):
        self.assertEqual("number", CONTACT_ROW_KEYS["phones"])
        self.assertEqual("mail_address", CONTACT_ROW_KEYS["mails"])
        self.assertEqual("url", CONTACT_ROW_KEYS["urls"])

    def test_row_key_strips(self):
        self.assertEqual("081", row_key("phones", {"number": "  081  "}))

    def test_row_key_of_a_row_without_its_key_column_is_empty(self):
        self.assertEqual("", row_key("phones", {"number": None}))
        self.assertEqual("", row_key("phones", {}))

    def test_row_key_uses_the_right_column_per_kind(self):
        self.assertEqual("a@b.be", row_key("mails", {"mail_address": "a@b.be"}))
        self.assertEqual("https://x", row_key("urls", {"url": "https://x"}))

    def test_columns_mirror_the_vocabularies(self):
        self.assertEqual(("label", "type", "number"), CONTACT_ROW_COLUMNS["phones"])
        self.assertEqual(
            ("label", "type", "mail_address"), CONTACT_ROW_COLUMNS["mails"]
        )
        self.assertEqual(("type", "url"), CONTACT_ROW_COLUMNS["urls"])


class TestTranslatedTypeLabel(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def test_empty_token_gives_empty_string(self):
        self.assertEqual("", translated_type_label("phones", ""))
        self.assertEqual("", translated_type_label("phones", None))

    def test_unknown_token_degrades_to_the_raw_token(self):
        # If the directory adds a type we do not know, the label degrades to the
        # token: visible but harmless.
        self.assertEqual(
            "carrier-pigeon", translated_type_label("phones", "carrier-pigeon")
        )

    def test_known_token_is_not_returned_raw(self):
        # The exact wording lives in imio.smartweb.locales; all we assert is
        # that a known token is resolved to something other than the token.
        label = translated_type_label("phones", "work")
        self.assertTrue(label)
        self.assertNotEqual("work", label)

    def test_a_token_known_for_another_kind_is_not_borrowed(self):
        # "facebook" is a url type, not a phone type.
        self.assertEqual("facebook", translated_type_label("phones", "facebook"))

    def test_an_unknown_kind_degrades_instead_of_raising(self):
        self.assertEqual("work", translated_type_label("bogus", "work"))


class TestBuildDisplayRows(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def test_rows_without_a_key_are_skipped(self):
        rows = build_display_rows("phones", [CONTACT])
        self.assertEqual(2, len(rows))
        self.assertEqual(["081 12 34 56", "0470 00 00 00"], [r["number"] for r in rows])

    def test_absent_preference_yields_every_column(self):
        rows = build_display_rows("phones", [CONTACT])
        self.assertEqual(["label", "type", "number"], list(rows[0]["visible_columns"]))

    def test_empty_preference_is_kept_empty(self):
        rows = build_display_rows("phones", [CONTACT], {("uid-1", "081 12 34 56"): []})
        self.assertEqual([], rows[0]["visible_columns"])
        # the other row keeps its default
        self.assertEqual(["label", "type", "number"], list(rows[1]["visible_columns"]))

    def test_partial_preference_is_carried_over(self):
        rows = build_display_rows(
            "phones", [CONTACT], {("uid-1", "081 12 34 56"): ["number"]}
        )
        self.assertEqual(["number"], rows[0]["visible_columns"])

    def test_each_row_owns_its_default_list(self):
        rows = build_display_rows("phones", [CONTACT])
        rows[0]["visible_columns"].append("bogus")
        self.assertEqual(["label", "type", "number"], list(rows[1]["visible_columns"]))

    def test_row_carries_contact_identity(self):
        rows = build_display_rows("phones", [CONTACT])
        self.assertEqual("uid-1", rows[0]["contact_uid"])
        self.assertEqual("Service culture", rows[0]["contact_title"])

    def test_type_column_is_translated_and_type_token_is_raw(self):
        rows = build_display_rows("phones", [CONTACT])
        self.assertEqual("work", rows[0]["type_token"])
        self.assertEqual(translated_type_label("phones", "work"), rows[0]["type"])
        self.assertEqual("cell", rows[1]["type_token"])

    def test_a_missing_data_column_becomes_an_empty_string(self):
        rows = build_display_rows("phones", [CONTACT])
        self.assertEqual("", rows[1]["label"])

    def test_no_contacts_gives_no_rows(self):
        self.assertEqual([], build_display_rows("phones", []))

    def test_a_contact_without_rows_of_that_kind_gives_no_rows(self):
        self.assertEqual([], build_display_rows("phones", [{"UID": "u", "title": "t"}]))

    def test_rows_of_several_contacts_are_concatenated_in_order(self):
        second = {
            "UID": "uid-2",
            "title": "Sports",
            "phones": [{"label": "", "type": "work", "number": "082"}],
        }
        rows = build_display_rows("phones", [CONTACT, second])
        self.assertEqual(["uid-1", "uid-1", "uid-2"], [r["contact_uid"] for r in rows])

    def test_preferences_are_keyed_per_contact(self):
        second = {
            "UID": "uid-2",
            "title": "Sports",
            "phones": [{"label": "", "type": "work", "number": "081 12 34 56"}],
        }
        # Same number on two different contacts: only uid-1's row is hidden.
        rows = build_display_rows(
            "phones", [CONTACT, second], {("uid-1", "081 12 34 56"): []}
        )
        by_uid = {(r["contact_uid"], r["number"]): r for r in rows}
        self.assertEqual([], by_uid[("uid-1", "081 12 34 56")]["visible_columns"])
        self.assertEqual(
            ["label", "type", "number"],
            list(by_uid[("uid-2", "081 12 34 56")]["visible_columns"]),
        )

    def test_mails_and_urls_kinds_build_their_own_columns(self):
        mails = build_display_rows("mails", [CONTACT])
        self.assertEqual("culture@ville.be", mails[0]["mail_address"])
        urls = build_display_rows("urls", [CONTACT])
        self.assertEqual("https://ville.be", urls[0]["url"])
        self.assertEqual("website", urls[0]["type_token"])


class TestGetRemoteContacts(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def test_no_uids_short_circuits_without_a_request(self):
        with mock.patch("imio.smartweb.common.contact.directory.get_json") as get_json:
            self.assertEqual([], get_remote_contacts([]))
            get_json.assert_not_called()

    def test_results_follow_the_requested_uid_order(self):
        payload = {"items": [{"UID": "b"}, {"UID": "a"}]}
        with mock.patch(
            "imio.smartweb.common.contact.directory.get_json", return_value=payload
        ):
            result = get_remote_contacts(["a", "b"])
        self.assertEqual(["a", "b"], [item["UID"] for item in result])

    def test_unrequested_uids_are_dropped(self):
        payload = {"items": [{"UID": "a"}, {"UID": "z"}]}
        with mock.patch(
            "imio.smartweb.common.contact.directory.get_json", return_value=payload
        ):
            result = get_remote_contacts(["a"])
        self.assertEqual(["a"], [item["UID"] for item in result])

    def test_directory_failure_gives_an_empty_list(self):
        with mock.patch(
            "imio.smartweb.common.contact.directory.get_json", return_value=None
        ):
            self.assertEqual([], get_remote_contacts(["a"]))

    def test_every_uid_is_passed_to_the_directory(self):
        with mock.patch(
            "imio.smartweb.common.contact.directory.get_json", return_value=None
        ) as get_json:
            get_remote_contacts(["a", "b"])
        url = get_json.call_args[0][0]
        self.assertIn("UID=a", url)
        self.assertIn("UID=b", url)
        self.assertIn("fullobjects=1", url)


class TestStoredPreferences(unittest.TestCase):
    def test_visible_columns_map_keys_on_uid_and_row_key(self):
        context = _Stored(
            phones_display=[
                {
                    "contact_uid": "uid-1",
                    "number": "081 12 34 56",
                    "visible_columns": ["number"],
                }
            ]
        )
        self.assertEqual(
            {("uid-1", "081 12 34 56"): ["number"]},
            visible_columns_map(context, "phones"),
        )

    def test_a_none_visible_columns_is_left_out_of_the_map(self):
        # "no preference recorded" must NOT be recorded as "explicitly hidden".
        context = _Stored(
            phones_display=[
                {"contact_uid": "uid-1", "number": "081", "visible_columns": None}
            ]
        )
        self.assertEqual({}, visible_columns_map(context, "phones"))

    def test_an_empty_visible_columns_is_recorded_as_empty(self):
        context = _Stored(
            phones_display=[
                {"contact_uid": "uid-1", "number": "081", "visible_columns": []}
            ]
        )
        self.assertEqual({("uid-1", "081"): []}, visible_columns_map(context, "phones"))

    def test_a_row_without_a_key_is_skipped(self):
        context = _Stored(
            phones_display=[
                {"contact_uid": "uid-1", "number": "", "visible_columns": []}
            ]
        )
        self.assertEqual({}, visible_columns_map(context, "phones"))

    def test_a_row_without_a_contact_uid_keys_on_the_empty_string(self):
        context = _Stored(phones_display=[{"number": "081", "visible_columns": []}])
        self.assertEqual({("", "081"): []}, visible_columns_map(context, "phones"))

    def test_missing_grid_attribute_gives_an_empty_map(self):
        self.assertEqual({}, visible_columns_map(_Stored(), "phones"))

    def test_a_none_grid_gives_an_empty_map(self):
        self.assertEqual(
            {}, visible_columns_map(_Stored(phones_display=None), "phones")
        )

    def test_the_returned_lists_are_copies(self):
        stored = ["number"]
        context = _Stored(
            phones_display=[
                {"contact_uid": "u", "number": "081", "visible_columns": stored}
            ]
        )
        visible_columns_map(context, "phones")[("u", "081")].append("bogus")
        self.assertEqual(["number"], stored)


class TestDisplayedRows(unittest.TestCase):
    def test_no_preference_shows_every_column(self):
        rows = displayed_rows(CONTACT, _Stored(), "phones")
        self.assertEqual(2, len(rows))
        self.assertEqual({"label", "type", "number"}, rows[0]["columns"])

    def test_an_explicitly_hidden_row_is_dropped(self):
        context = _Stored(
            phones_display=[
                {
                    "contact_uid": "uid-1",
                    "number": "081 12 34 56",
                    "visible_columns": [],
                }
            ]
        )
        rows = displayed_rows(CONTACT, context, "phones")
        self.assertEqual(["0470 00 00 00"], [r["data"]["number"] for r in rows])

    def test_columns_are_intersected_with_the_known_ones(self):
        context = _Stored(
            phones_display=[
                {
                    "contact_uid": "uid-1",
                    "number": "081 12 34 56",
                    "visible_columns": ["number", "bogus"],
                }
            ]
        )
        rows = displayed_rows(CONTACT, context, "phones")
        self.assertEqual({"number"}, rows[0]["columns"])

    def test_a_preference_recorded_for_another_contact_does_not_apply(self):
        context = _Stored(
            phones_display=[
                {
                    "contact_uid": "other-uid",
                    "number": "081 12 34 56",
                    "visible_columns": [],
                }
            ]
        )
        rows = displayed_rows(CONTACT, context, "phones")
        self.assertEqual(2, len(rows))

    def test_the_remote_row_is_returned_as_is(self):
        # It belongs to cached JSON and must not be copied or mutated.
        rows = displayed_rows(CONTACT, _Stored(), "phones")
        self.assertIs(CONTACT["phones"][0], rows[0]["data"])

    def test_a_payload_without_rows_of_that_kind_gives_no_rows(self):
        self.assertEqual([], displayed_rows({"UID": "u"}, _Stored(), "phones"))
