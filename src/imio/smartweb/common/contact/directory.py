# -*- coding: utf-8 -*-

from imio.smartweb.common.config import DIRECTORY_URL
from imio.smartweb.common.utils import get_json
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from zope.i18n import translate

# Human labels of the remote `type` tokens. The directory owns these
# vocabularies (imio/directory/core/vocabularies.py); their msgids live in the
# shared `imio.smartweb` domain, so they can be reused here without depending
# on imio.directory.core. If the directory adds a type, its label degrades to
# the raw token -- visible but harmless.
CONTACT_TYPE_LABELS = {
    "phones": {
        "fax": _("Fax"),
        "cell": _("Mobile"),
        "home": _("Personal phone"),
        "work": _("Work phone"),
    },
    "mails": {
        "home": _("Personal email"),
        "work": _("Work email"),
    },
    "urls": {
        "facebook": _("Facebook"),
        "instagram": _("Instagram"),
        "linkedin": _("Linkedin"),
        "pinterest": _("Pinterest"),
        "twitter": _("Twitter"),
        "website": _("Website"),
        "youtube": _("Youtube"),
    },
}

# The remote column that identifies a row. A row without it cannot be keyed,
# so no preference can be recorded for it and it is skipped.
CONTACT_ROW_KEYS = {
    "phones": "number",
    "mails": "mail_address",
    "urls": "url",
}

# Columns of each row, in display order. Must mirror the *DisplayColumns
# vocabularies token for token.
CONTACT_ROW_COLUMNS = {
    "phones": ("label", "type", "number"),
    "mails": ("label", "type", "mail_address"),
    "urls": ("type", "url"),
}


def translated_type_label(kind, token):
    """Human label of a remote `type` token, or the raw token if unknown."""
    if not token:
        return ""
    msgid = CONTACT_TYPE_LABELS.get(kind, {}).get(token)
    if msgid is None:
        return token
    current_lang = api.portal.get_current_language()[:2]
    return translate(msgid, target_language=current_lang)


def row_key(kind, row):
    """Identity of a remote row: its payload value, or "" when it has none."""
    return (row.get(CONTACT_ROW_KEYS[kind]) or "").strip()


def build_display_rows(kind, contacts, preferences=None):
    """Build the DataGridField rows of `kind` from remote contact payloads.

    `contacts` is a list of contact dicts as returned by
    `@search?UID=...&fullobjects=1`. `preferences` maps
    `(contact_uid, row_key)` to a list of column names to carry over.

    A key ABSENT from `preferences` means "no preference recorded" and yields
    every column. A key present with an EMPTY list means "explicitly hidden"
    and is kept as such. The two are not interchangeable.
    """
    preferences = preferences or {}
    all_columns = CONTACT_ROW_COLUMNS[kind]
    rows = []
    for contact in contacts:
        uid = contact.get("UID") or ""
        title = contact.get("title") or ""
        for remote_row in contact.get(kind) or []:
            key = row_key(kind, remote_row)
            if not key:
                continue
            row = {
                "contact_uid": uid,
                "contact_title": title,
                # The raw token, kept alongside the translated `type` label so
                # a consumer that publishes the STORED row is not stuck with
                # the editor's language. See _ContactRowBase.type_token.
                "type_token": remote_row.get("type") or "",
                # list() so each row owns its default.
                "visible_columns": list(preferences.get((uid, key), all_columns)),
            }
            for column in all_columns:
                if column == "type":
                    row["type"] = translated_type_label(kind, remote_row.get("type"))
                else:
                    row[column] = remote_row.get(column) or ""
            rows.append(row)
    return rows


def get_remote_contacts(uids):
    """Live directory payload for `uids`, in that order.

    Deliberately uncached: this is only called from the "load contact
    informations" button, where the editor is asking for fresh data.
    """
    if not uids:
        return []
    url = "{}/@search?UID={}&fullobjects=1".format(DIRECTORY_URL, "&UID=".join(uids))
    current_lang = api.portal.get_current_language()[:2]
    if current_lang != "fr":
        url = f"{url}&translated_in_{current_lang}=1"
    json_data = get_json(url)
    if not json_data:
        return []
    index_map = {uid: index for index, uid in enumerate(uids)}
    items = [
        item for item in json_data.get("items") or [] if item.get("UID") in index_map
    ]
    return sorted(items, key=lambda item: index_map[item["UID"]])


def visible_columns_map(context, kind):
    """{(contact_uid, row_key): [column, ...]} from the stored preferences.

    A key ABSENT from the returned map means "no preference recorded" and
    yields every column at render time. A key present with an EMPTY list
    means "explicitly hidden" and drops the row. The two are NOT
    interchangeable: never normalise one into the other. A stored row whose
    `visible_columns` is None is treated as "no preference", so its key is
    deliberately left out of the map.
    """
    stored = getattr(context, f"{kind}_display", None) or []
    result = {}
    for row in stored:
        key = row_key(kind, row)
        if not key:
            continue
        columns = row.get("visible_columns")
        if columns is None:
            continue
        result[(row.get("contact_uid") or "", key)] = list(columns)
    return result


def displayed_rows(payload, context, kind):
    """Remote rows of `kind`, each with the set of columns to render.

    Returns [{"data": <remote row dict>, "columns": <set of names>}, ...].
    Rows explicitly hidden are omitted, as are rows with no usable key.

    `payload` is the LIVE directory payload: the stored `*_display` data
    columns are residue for this function and are never read here. The remote
    row dict is returned as-is and must not be mutated -- it belongs to cached
    JSON.
    """
    preferences = visible_columns_map(context, kind)
    uid = payload.get("UID") or ""
    all_columns = set(CONTACT_ROW_COLUMNS[kind])
    rows = []
    for remote_row in payload.get(kind) or []:
        key = row_key(kind, remote_row)
        if not key:
            continue
        columns = preferences.get((uid, key))
        if columns is None:
            columns = set(all_columns)
        else:
            columns = set(columns) & all_columns
            if not columns:
                continue
        rows.append({"data": remote_row, "columns": columns})
    return rows
