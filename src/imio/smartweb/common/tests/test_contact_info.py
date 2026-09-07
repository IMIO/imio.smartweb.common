# -*- coding: utf-8 -*-

from imio.smartweb.common.config import DIRECTORY_URL
from imio.smartweb.common.interfaces import ILocalManagerAware
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser
from unittest.mock import MagicMock
from unittest.mock import patch
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import json
import transaction
import unittest

# The two views proxy the remote directory through
# imio.smartweb.common.utils.get_json, so ``requests.get`` is the only thing
# mocked: get_json itself (status handling, JSON parsing) and the URLs the views
# build are exercised for real.
REQUESTS_GET = "imio.smartweb.common.utils.requests.get"


class DirectoryInfoTestCase(unittest.TestCase):
    """Shared fixture for both views of ``browser/contact_info.py``."""

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request.form.clear()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # Stand in for the consuming packages' Entity: the views resolve their
        # scope from ILocalManagerAware, which only Entity provides there.
        self.entity = api.content.create(
            container=self.portal, type="Folder", id="entity", title="Entity"
        )
        alsoProvides(self.entity, ILocalManagerAware)
        self.content = api.content.create(
            container=self.entity, type="Folder", id="content", title="Content"
        )

    def make_view(self, context, name):
        return getMultiAdapter((context, self.request), name=name)

    def fake_response(self, payload, status_code=200):
        """Stand in for a ``requests`` response as get_json consumes it."""
        response = MagicMock()
        response.status_code = status_code
        response.text = json.dumps(payload)
        return response


class TestDirectoryContactInfoView(DirectoryInfoTestCase):
    def make_view(self, context=None):
        return super().make_view(
            context if context is not None else self.content,
            "directory_contact_info",
        )

    def contact_payload(self, **contact):
        """A directory @search result holding a single contact."""
        return {"items": [contact], "items_total": 1}

    def test_no_uid_returns_empty_json(self):
        with patch(REQUESTS_GET) as mock_get:
            result = json.loads(self.make_view()())
        self.assertEqual(result, {})
        # Without a uid there is nothing to look up: the directory is not called.
        mock_get.assert_not_called()

    def test_response_is_flagged_as_json(self):
        self.make_view()()
        self.assertEqual(
            self.request.response.getHeader("Content-Type"), "application/json"
        )

    def test_returns_contact_and_address_fields(self):
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(
            **{
                "@id": "https://annuaire.enwallonie.be/mons/contact-uid",
                "title": "Centre culturel",
                "street": "rue de Nimy",
                "number": "106",
                "complement": "boîte 2",
                "zipcode": "7000",
                "city": "Mons",
                "country": {"title": "Belgique", "token": "be"},
                "phones": [{"label": None, "number": "+3265000000", "type": "work"}],
                "mails": [
                    {"label": None, "mail_address": "info@ccmons.be", "type": "work"}
                ],
            }
        )
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(
            result,
            {
                "url": "https://annuaire.enwallonie.be/mons/contact-uid",
                "name": "Centre culturel",
                "email": "info@ccmons.be",
                "phone": "+3265000000",
                "street": "rue de Nimy",
                "number": "106",
                "complement": "boîte 2",
                "zipcode": "7000",
                "city": "Mons",
                "country": "be",
            },
        )

    def test_name_combines_title_and_subtitle(self):
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(title="Centre culturel", subtitle="Billetterie")
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result["name"], "Centre culturel: Billetterie")

    def test_name_ignores_empty_subtitle(self):
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(title="Centre culturel", subtitle=None)
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result["name"], "Centre culturel")

    def test_country_falls_back_to_title_without_token(self):
        # A serializer variant that only exposes the human-readable label.
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(country={"title": "Belgique"})
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result["country"], "Belgique")

    def test_country_token_is_kept_as_is_when_not_a_dict(self):
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(country="be")
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result["country"], "be")

    def test_unset_fields_are_normalised_to_empty_strings(self):
        # What the real directory returns for a contact whose address, phones
        # and mails were never filled in: every key present, every value None.
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(
            **{
                "@id": None,
                "title": "FEDER",
                "subtitle": None,
                "street": None,
                "number": None,
                "complement": None,
                "zipcode": None,
                "city": None,
                "country": None,
                "phones": None,
                "mails": None,
            }
        )
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result.pop("name"), "FEDER")
        self.assertEqual(set(result.values()), {""})

    def test_legacy_integer_zipcode_is_coerced_to_string(self):
        # ``zipcode`` is a TextLine today, but records created when it was an
        # Int may still hold one.
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(zipcode=5300)
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result["zipcode"], "5300")

    def test_first_phone_and_mail_win(self):
        self.request.form["uid"] = "contact-uid"
        payload = self.contact_payload(
            phones=[{"number": "+3265000000"}, {"number": "+3265999999"}],
            mails=[{"mail_address": "first@ccmons.be"}, {"mail_address": "b@c.be"}],
        )
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result["phone"], "+3265000000")
        self.assertEqual(result["email"], "first@ccmons.be")

    def test_unknown_uid_returns_empty_json(self):
        self.request.form["uid"] = "gone"
        payload = {"items": [], "items_total": 0}
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(result, {})

    def test_unreachable_directory_returns_empty_json(self):
        self.request.form["uid"] = "contact-uid"
        with patch(REQUESTS_GET, return_value=self.fake_response({}, status_code=503)):
            result = json.loads(self.make_view()())
        self.assertEqual(result, {})

    def test_searches_the_directory_on_the_contact_uid(self):
        self.request.form["uid"] = "contact uid/with specials"
        with patch(
            REQUESTS_GET, return_value=self.fake_response(self.contact_payload())
        ) as mock_get:
            self.make_view()()
        self.assertEqual(
            mock_get.call_args[0][0],
            "{}/@search?UID={}&fullobjects=true".format(
                DIRECTORY_URL, "contact uid/with specials"
            ),
        )

    def test_cache_buster_is_forwarded_to_the_directory(self):
        # The "Refresh" button sends "_=<timestamp>" so no cache in front of the
        # directory can serve a contact that was just edited there.
        self.request.form["uid"] = "contact-uid"
        self.request.form["_"] = "1755000000000"
        with patch(
            REQUESTS_GET, return_value=self.fake_response(self.contact_payload())
        ) as mock_get:
            self.make_view()()
        self.assertEqual(
            mock_get.call_args[0][0],
            "{}/@search?UID=contact-uid&fullobjects=true&_=1755000000000".format(
                DIRECTORY_URL
            ),
        )

    def test_no_cache_buster_leaves_the_url_untouched(self):
        self.request.form["uid"] = "contact-uid"
        with patch(
            REQUESTS_GET, return_value=self.fake_response(self.contact_payload())
        ) as mock_get:
            self.make_view()()
        self.assertNotIn("&_=", mock_get.call_args[0][0])


class TestDirectoryLinkedEntitiesInfoView(DirectoryInfoTestCase):
    def make_view(self, context=None):
        return super().make_view(
            context if context is not None else self.content,
            "directory_entities_info",
        )

    def entities_payload(self, *entities):
        return {"items": list(entities), "items_total": len(entities)}

    def test_returns_empty_list_outside_an_entity(self):
        with patch(REQUESTS_GET) as mock_get:
            result = json.loads(self.make_view(self.portal)())
        self.assertEqual(result, [])
        mock_get.assert_not_called()

    def test_response_is_flagged_as_json(self):
        self.make_view()()
        self.assertEqual(
            self.request.response.getHeader("Content-Type"), "application/json"
        )

    def test_returns_empty_list_without_linked_entities(self):
        # Plain Folder, not the consuming packages' Entity: no schema field to
        # guarantee the attribute exists, hence getattr with a default here
        # (unlike the original imio.events.core fixture).
        self.assertFalse(getattr(self.entity, "directory_linked_entities", None))
        with patch(REQUESTS_GET) as mock_get:
            result = json.loads(self.make_view()())
        self.assertEqual(result, [])
        mock_get.assert_not_called()

    def test_returns_title_and_url_of_each_linked_entity(self):
        self.entity.directory_linked_entities = ["uid1", "uid2"]
        payload = self.entities_payload(
            {"@id": "https://annuaire.enwallonie.be/mons", "title": "Mons"},
            {"@id": "https://annuaire.enwallonie.be/namur", "title": "Namur"},
        )
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(
            result,
            [
                {"title": "Mons", "url": "https://annuaire.enwallonie.be/mons"},
                {"title": "Namur", "url": "https://annuaire.enwallonie.be/namur"},
            ],
        )

    def test_skips_entities_without_url(self):
        self.entity.directory_linked_entities = ["uid1", "uid2"]
        payload = self.entities_payload(
            {"@id": None, "title": "Sans URL"},
            {"@id": "https://annuaire.enwallonie.be/mons", "title": "Mons"},
        )
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(
            result, [{"title": "Mons", "url": "https://annuaire.enwallonie.be/mons"}]
        )

    def test_missing_title_is_normalised_to_an_empty_string(self):
        self.entity.directory_linked_entities = ["uid1"]
        payload = self.entities_payload(
            {"@id": "https://annuaire.enwallonie.be/mons", "title": None}
        )
        with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
            result = json.loads(self.make_view()())
        self.assertEqual(
            result, [{"title": "", "url": "https://annuaire.enwallonie.be/mons"}]
        )

    def test_unreachable_directory_returns_empty_list(self):
        self.entity.directory_linked_entities = ["uid1"]
        with patch(REQUESTS_GET, return_value=self.fake_response({}, status_code=503)):
            result = json.loads(self.make_view()())
        self.assertEqual(result, [])

    def test_asks_the_directory_for_every_linked_entity_at_once(self):
        self.entity.directory_linked_entities = ["uid1", "uid2"]
        with patch(
            REQUESTS_GET, return_value=self.fake_response(self.entities_payload())
        ) as mock_get:
            self.make_view()()
        # Repeated UID params are OR-ed by the catalog, hence a single request.
        self.assertEqual(
            mock_get.call_args[0][0],
            "{}/@search?portal_type=imio.directory.Entity&sort_on=sortable_title"
            "&b_size=3000&metadata_fields=UID&UID=uid1&UID=uid2".format(DIRECTORY_URL),
        )

    def test_looks_up_the_entity_from_a_nested_context(self):
        # The view is called on <body data-base-url>, i.e. the Event on an edit
        # form and the container Agenda on an add form: both must resolve the
        # same parent Entity.
        self.entity.directory_linked_entities = ["uid1"]
        payload = self.entities_payload(
            {"@id": "https://annuaire.enwallonie.be/mons", "title": "Mons"}
        )
        for context in (self.entity, self.entity, self.content):
            with patch(REQUESTS_GET, return_value=self.fake_response(payload)):
                result = json.loads(self.make_view(context)())
            self.assertEqual(
                result,
                [{"title": "Mons", "url": "https://annuaire.enwallonie.be/mons"}],
                "unexpected result for context {}".format(context.portal_type),
            )


class TestDirectoryInfoViewsAccess(unittest.TestCase):
    """Both proxy views must be reachable by the editors that use the edit form.

    The edit-form JS calls ``@@directory_contact_info`` on the *portal root*
    (``<body data-portal-url>``), so the view's permission has to be one a plain
    editor holds there -- not only a Manager.
    """

    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal, type="Folder", id="entity", title="Entity"
        )
        alsoProvides(self.entity, ILocalManagerAware)
        self.content = api.content.create(
            container=self.entity, type="Folder", id="content", title="Content"
        )
        # A real editor of this entity: no global role, only local roles on the
        # entity -- exactly what a communal editor gets on this platform.
        api.user.create(
            username="editor", email="editor@example.com", password="secret123"
        )
        api.user.grant_roles(
            username="editor",
            obj=self.entity,
            roles=["Reader", "Contributor", "Editor"],
        )
        self.entity.reindexObjectSecurity()
        transaction.commit()

    def browser(self, username=None, password=None):
        browser = Browser(self.app)
        if username:
            browser.addHeader("Authorization", "Basic {}:{}".format(username, password))
        return browser

    def test_editor_can_read_contact_info_on_the_portal_root(self):
        browser = self.browser("editor", "secret123")
        browser.open("{}/@@directory_contact_info".format(self.portal.absolute_url()))
        self.assertEqual(json.loads(browser.contents), {})

    def test_editor_can_read_entities_info_on_the_event(self):
        browser = self.browser("editor", "secret123")
        browser.open("{}/@@directory_entities_info".format(self.content.absolute_url()))
        self.assertEqual(json.loads(browser.contents), [])

    def test_anonymous_cannot_read_contact_info(self):
        # The view is a proxy to the remote directory: keep it out of reach of
        # anonymous visitors, who have no edit form to fill in anyway.
        browser = self.browser()
        browser.open("{}/@@directory_contact_info".format(self.portal.absolute_url()))
        self.assertIn("/login", browser.url)

    def test_anonymous_cannot_read_entities_info(self):
        browser = self.browser()
        browser.open("{}/@@directory_entities_info".format(self.content.absolute_url()))
        self.assertIn("/login", browser.url)


# <audit>
# Task 3 (WEBBDC-2790): moved the directory proxy views browser/contact_info.py
# from imio.events.core to imio.smartweb.common, made them generic.
#
# - browser/contact_info.py: replaced the IEntity import/usage with the shared
#   ILocalManagerAware marker interface; `entity.directory_linked_entities`
#   became `getattr(entity, "directory_linked_entities", None)` since the
#   common package has no Entity schema to guarantee the attribute; docstrings
#   no longer mention "Event"/"IEventContact" since the views are generic now;
#   both `__call__` methods now build their search URL from
#   `imio.smartweb.common.utils.get_directory_url()` instead of the
#   `DIRECTORY_URL` constant directly, so a registry override
#   (`imio.smartweb.common.directory_url`) is honoured by the proxy views too.
# - browser/configure.zcml: registered `directory_contact_info` and
#   `directory_entities_info` as `browser:page for="*"`,
#   `permission="zope2.View"`, on `IImioSmartwebCommonLayer`.
# - tests/test_contact_info.py: same 28 test methods across the same 3 test
#   classes (15 + 9 + 4), only the fixture changed: Entity/Agenda/Event became
#   a two-level Folder/Folder tree (`self.entity`, marked with
#   `alsoProvides(self.entity, ILocalManagerAware)`, and `self.content` inside
#   it), replacing `self.agenda` with `self.entity` and `self.event` with
#   `self.content` throughout. In the functional test class, `alsoProvides`
#   is called before `transaction.commit()` so the marker is visible to the
#   real publication request `zope.testbrowser` makes.
#
# Deviation from the brief, required to keep all 28 tests green: in
# TestDirectoryLinkedEntitiesInfoView.test_returns_empty_list_without_linked_entities,
# `self.assertFalse(self.entity.directory_linked_entities)` read the attribute
# directly off a plain Folder, which (unlike imio.events.Entity) has no such
# schema field and so raised AttributeError instead of returning None. Changed
# to `getattr(self.entity, "directory_linked_entities", None)`, mirroring the
# same accommodation already made in browser/contact_info.py's
# DirectoryLinkedEntitiesInfoView.__call__ for the identical reason.
# </audit>
