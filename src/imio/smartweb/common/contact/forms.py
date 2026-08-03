# -*- coding: utf-8 -*-

from imio.smartweb.common.contact.directory import build_display_rows
from imio.smartweb.common.contact.directory import CONTACT_ROW_COLUMNS
from imio.smartweb.common.contact.directory import CONTACT_ROW_KEYS
from imio.smartweb.common.contact.directory import get_remote_contacts
from imio.smartweb.common.widgets.select import TranslatedAjaxSelectWidget
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api

DISPLAY_FIELDS = ("phones_display", "mails_display", "urls_display")

# A multi-valued AjaxSelectWidget submits ONE text input holding every selected
# UID joined by this separator, not a list. Reading the raw request value
# without splitting would build a single bogus "uid1;uid2" UID.
CONTACT_UIDS_SEPARATOR = TranslatedAjaxSelectWidget.separator

KIND_BY_FIELD = {
    "phones_display": "phones",
    "mails_display": "mails",
    "urls_display": "urls",
}

# Columns written for every row on top of the kind's own data columns. They are
# hidden or frozen in the form but must still be submitted: DictRow rejects a
# row whose keys are missing.
EXTRA_ROW_COLUMNS = ("contact_uid", "contact_title", "type_token")


class ContactInformationsGridMixin:
    """Repopulates the read-only contact-informations grids from the directory.

    The grids are never "filled once": they are derived from the contacts
    currently selected in `contact_uids_field`. Rather than rebuilding widgets,
    this rewrites the request BEFORE super().update(), so the normal
    request -> widget path regenerates names, ids, the .count marker and the
    patterns by construction.

    Subclasses set `contact_uids_field` to the name of their own schema field
    holding the contact UID(s): a multi-valued list (imio.smartweb.core's
    Section contact) or a single Choice (imio.events.core's Secondary contact).
    Both submission shapes are handled.
    """

    contact_uids_field = "related_contacts"

    def update(self):
        if self.request.form.get(self._load_button_name):
            self._reload_display_grids()
        super().update()

    @property
    def _load_button_name(self):
        return "{}buttons.load_contact_informations".format(self.prefix)

    def _reload_display_grids(self):
        uids = self._submitted_contact_uids()
        if not uids:
            api.portal.show_message(
                _("Please select a contact before loading its information."),
                request=self.request,
                type="info",
            )
            contacts = []
        else:
            contacts = get_remote_contacts(uids)
            if not contacts:
                # get_remote_contacts returns [] for a timeout, a non-200 and
                # an unreachable host alike (utils.get_json swallows every
                # exception), so "UIDs submitted but nothing came back" can
                # only be a failure. Rewriting the grids here would empty them
                # and destroy every recorded visible_columns preference on the
                # next save, so leave the request untouched.
                api.portal.show_message(
                    _(
                        "The contact directory could not be reached: contact "
                        "information was not loaded and nothing was changed."
                    ),
                    request=self.request,
                    type="error",
                )
                return
            api.portal.show_message(
                _("Contact information has been loaded."),
                request=self.request,
                type="info",
            )
        for field_name in DISPLAY_FIELDS:
            kind = KIND_BY_FIELD[field_name]
            prefix = "{}widgets.{}".format(self.prefix, field_name)
            preferences = self._extract_preferences(prefix, kind)
            rows = build_display_rows(kind, contacts, preferences)
            self._write_grid(prefix, kind, rows)

    def _submitted_contact_uids(self):
        """UIDs currently selected, in order.

        A multi-valued AjaxSelectWidget submits them as a single
        separator-joined string; a single-valued select submits one plain
        value; a plain list is accepted too, so the method does not depend on
        the widget in use.
        """
        uids = self.request.form.get(
            "{}widgets.{}".format(self.prefix, self.contact_uids_field)
        )
        if isinstance(uids, str):
            uids = uids.split(CONTACT_UIDS_SEPARATOR)
        return [uid.strip() for uid in uids or [] if uid and uid.strip()]

    def _extract_preferences(self, prefix, kind):
        """Checkbox state already in the request, keyed (contact_uid, row_key).

        A row whose checkbox group submitted nothing yields an EMPTY list --
        "explicitly hidden" -- not a missing key. The widget was rendered (we
        only look at indices whose contact_uid is present), so "nothing
        submitted" can only mean "everything unchecked".
        """
        form = self.request.form
        key_column = CONTACT_ROW_KEYS[kind]
        preferences = {}
        index = 0
        while "{}.{}.widgets.contact_uid".format(prefix, index) in form:
            row_prefix = "{}.{}.widgets".format(prefix, index)
            key = (form.get("{}.{}".format(row_prefix, key_column)) or "").strip()
            if key:
                columns = form.get("{}.visible_columns".format(row_prefix))
                if columns is None:
                    columns = []
                elif isinstance(columns, str):
                    columns = [columns]
                uid = form.get("{}.contact_uid".format(row_prefix)) or ""
                preferences[(uid, key)] = list(columns)
            index += 1
        return preferences

    def _write_grid(self, prefix, kind, rows):
        form = self.request.form
        for key in [key for key in form if key.startswith("{}.".format(prefix))]:
            del form[key]
        columns = EXTRA_ROW_COLUMNS + CONTACT_ROW_COLUMNS[kind]
        for index, row in enumerate(rows):
            row_prefix = "{}.{}.widgets".format(prefix, index)
            for column in columns:
                form["{}.{}".format(row_prefix, column)] = row.get(column) or ""
            form["{}.visible_columns".format(row_prefix)] = list(row["visible_columns"])
            form["{}.visible_columns-empty-marker".format(row_prefix)] = "1"
        form["{}.count".format(prefix)] = str(len(rows))
