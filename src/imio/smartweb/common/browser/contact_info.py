# -*- coding: utf-8 -*-
import json

from AccessControl import Unauthorized
from imio.smartweb.common.interfaces import ILocalManagerAware
from imio.smartweb.common.utils import get_directory_url
from imio.smartweb.common.utils import get_json
from imio.smartweb.common.utils import get_parent_providing
from plone import api
from Products.Five.browser import BrowserView


def guard_anonymous():
    """Both views proxy the remote directory for the add/edit form.

    They are registered with ``zope2.View`` so that an editor holding only
    local roles on an Entity can call them on the portal root (see
    browser/configure.zcml), which means the anonymous case has to be refused
    here rather than by the ZCML permission.
    """
    if api.user.is_anonymous():
        raise Unauthorized


class DirectoryContactInfoView(BrowserView):
    """Return the linked contact's name/email/phone as JSON.

    Used by the add/edit form JS to autofill the contact fields when
    the user picks an entry in ``directory_linked_contact``.
    """

    def __call__(self):
        guard_anonymous()
        self.request.response.setHeader("Content-Type", "application/json")
        uid = self.request.form.get("uid")
        if not uid:
            return json.dumps({})
        url = "{}/@search?UID={}&fullobjects=true".format(get_directory_url(), uid)
        # Forward the JS cache-buster (refresh button sends "_=<timestamp>") to
        # the directory so no proxy in front of it can serve a stale copy of a
        # contact that was just edited there.
        nocache = self.request.form.get("_")
        if nocache:
            url += "&_={}".format(nocache)
        data = get_json(url, None, 12)
        items = (data or {}).get("items") or []
        if not items:
            return json.dumps({})
        contact = items[0]
        phones = contact.get("phones") or []
        mails = contact.get("mails") or []
        contact_title = contact.get("title") or ""
        contact_subtitle = contact.get("subtitle") or ""
        if contact_subtitle != "":
            contact_name = f"{contact_title}: {contact_subtitle}"
        else:
            contact_name = contact_title
        # IAddress fields are identical on Event and Contact. ``country`` comes
        # back as a {"title": ..., "token": ...} dict whose token (e.g. "be")
        # matches the option values of the Event's country select (built from
        # imio.smartweb.vocabulary.Countries, lowercase ISO codes). ``zipcode``
        # is a TextLine on both sides today, but old records may still hold the
        # int it used to be, so coerce it for the text input.
        country = contact.get("country") or ""
        if isinstance(country, dict):
            country = country.get("token") or country.get("title") or ""
        zipcode = contact.get("zipcode")
        result = {
            # Canonical directory URL of the contact (already points inside its
            # own entity). The edit form JS appends "/edit" to build a link that
            # opens the contact for editing in the remote directory.
            "url": contact.get("@id") or "",
            "name": contact_name,
            "email": (mails[0].get("mail_address") if mails else "") or "",
            "phone": (phones[0].get("number") if phones else "") or "",
            "street": contact.get("street") or "",
            "number": contact.get("number") or "",
            "complement": contact.get("complement") or "",
            "zipcode": "" if zipcode is None else str(zipcode),
            "city": contact.get("city") or "",
            "country": country,
        }
        return json.dumps(result)


class DirectoryLinkedEntitiesInfoView(BrowserView):
    """Return the parent Entity's linked directory entities as JSON.

    Used by the add/edit form JS to build "add a new contact" links: one
    per directory entity linked on the parent Entity, each pointing at the
    entity's real directory URL (its ``@id``) plus ``/++add++imio.directory.Contact``.
    Called on the content context (via <body data-base-url>), not the portal
    root, because the linked entities depend on the parent Entity.
    """

    def __call__(self):
        guard_anonymous()
        self.request.response.setHeader("Content-Type", "application/json")
        entity = get_parent_providing(self.context, ILocalManagerAware)
        if entity is None:
            return json.dumps([])
        uids = getattr(entity, "directory_linked_entities", None) or []
        if not uids:
            return json.dumps([])
        params = [
            "portal_type=imio.directory.Entity",
            "sort_on=sortable_title",
            "b_size=3000",
            "metadata_fields=UID",
        ]
        # Repeated UID params are OR-ed by the catalog, so we get every linked
        # entity in one request.
        params.extend("UID={}".format(uid) for uid in uids)
        url = "{}/@search?{}".format(get_directory_url(), "&".join(params))
        data = get_json(url, None, 12)
        items = (data or {}).get("items") or []
        result = [
            {"title": item.get("title") or "", "url": item.get("@id") or ""}
            for item in items
            if item.get("@id")
        ]
        return json.dumps(result)
