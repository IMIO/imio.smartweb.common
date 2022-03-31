# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import ILocalManagerAware
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.workflow.permissions import DelegateRoles
from plone.testing.zope import Browser
from Products.CMFCore.utils import _checkPermission
from zope.interface import alsoProvides

import transaction
import unittest


class TestLocalRoles(unittest.TestCase):

    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
        )

    def test_sharing_page_available(self):
        alsoProvides(self.folder, ILocalManagerAware)
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        browser.open("{}/@@sharing".format(self.folder.absolute_url()))
        content = browser.contents
        self.assertIn("Insufficient Privileges", content)

        self.folder.manage_setLocalRoles(TEST_USER_ID, ("Local Manager",))
        transaction.commit()
        browser.open("{}/@@sharing".format(self.folder.absolute_url()))
        content = browser.contents
        self.assertIn("Can add", content)
        self.assertIn("Can edit", content)
        self.assertIn("Can manage locally", content)
        self.assertIn("Can review", content)
        self.assertIn("Can view", content)
        self.assertNotIn("Insufficient Privileges", content)

        transaction.commit()
        browser.open("{}/@@sharing".format(self.portal.absolute_url()))
        content = browser.contents
        self.assertIn("Insufficient Privileges", content)

    def test_delegate_sharing_permission(self):
        self.assertTrue(_checkPermission(DelegateRoles, self.folder))
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        self.assertFalse(_checkPermission(DelegateRoles, self.folder))
        setRoles(self.portal, TEST_USER_ID, ["Local Manager"])
        self.assertTrue(_checkPermission(DelegateRoles, self.folder))

    def test_local_manager_in_sharing(self):
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        browser.open("{}/@@sharing".format(self.folder.absolute_url()))
        content = browser.contents
        self.assertNotIn("Can manage locally", content)

        alsoProvides(self.folder, ILocalManagerAware)
        transaction.commit()
        browser.open("{}/@@sharing".format(self.folder.absolute_url()))
        content = browser.contents
        self.assertIn("Can manage locally", content)
