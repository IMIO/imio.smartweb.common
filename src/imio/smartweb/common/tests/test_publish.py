# -*- coding: utf-8 -*-

from imio.smartweb.common.behaviors.publish import ISaveAndPublish
from imio.smartweb.common.behaviors.publish import publish
from imio.smartweb.common.behaviors.publish import publish_transition
from imio.smartweb.common.behaviors.publish import type_can_publish
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.statusmessages.interfaces import IStatusMessage

import unittest


class TestPublish(unittest.TestCase):
    """The behavior is activated on Document only, by the testing profile."""

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.document = api.content.create(
            container=self.portal, type="Document", title="Document"
        )
        self.folder = api.content.create(
            container=self.portal, type="Folder", title="Folder"
        )

    def test_behavior_marks_content(self):
        self.assertTrue(ISaveAndPublish.providedBy(self.document))
        self.assertFalse(ISaveAndPublish.providedBy(self.folder))

    def test_publish_transition(self):
        self.assertEqual(publish_transition(self.document), "publish")
        # Without the behavior there is nothing to offer, workflow or not.
        self.assertIsNone(publish_transition(self.folder))
        # Already published: no transition left leading to "published".
        api.content.transition(obj=self.document, transition="publish")
        self.assertIsNone(publish_transition(self.document))

    def test_publish_transition_follows_user_permissions(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        self.assertIsNone(publish_transition(self.document))

    def test_type_can_publish(self):
        self.assertTrue(type_can_publish("Document", self.portal))
        self.assertFalse(type_can_publish("Folder", self.portal))
        self.assertFalse(type_can_publish("Unknown.Type", self.portal))

    def test_type_can_publish_follows_user_permissions(self):
        # An editor may create a Document but not publish it: the add form must
        # not offer the button at all.
        setRoles(self.portal, TEST_USER_ID, ["Contributor", "Editor"])
        self.assertFalse(type_can_publish("Document", self.portal))
        setRoles(self.portal, TEST_USER_ID, ["Reviewer"])
        self.assertTrue(type_can_publish("Document", self.portal))

    def test_publish(self):
        publish(self.document, "publish", self.request)
        self.assertEqual(api.content.get_state(self.document), "published")

    def test_publish_ignores_a_missing_transition(self):
        # Belt and braces: the button is hidden from users who may not publish,
        # so this path stays silent instead of reporting anything to them.
        publish(self.document, None, self.request)
        self.assertEqual(api.content.get_state(self.document), "private")
        self.assertEqual(IStatusMessage(self.request).show(), [])

    def test_publish_warns_instead_of_failing(self):
        publish(self.document, "unknown_transition", self.request)
        self.assertEqual(api.content.get_state(self.document), "private")
        self.assertEqual(IStatusMessage(self.request).show()[-1].type, "warning")
