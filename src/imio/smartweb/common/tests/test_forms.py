# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser

import transaction
import unittest


class TestForms(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_leadimage_caption_field(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder",
        )
        self.check_leadimage_caption_field(folder, container=self.portal)
        document = api.content.create(
            container=folder,
            type="Document",
            title="Document",
        )
        self.check_leadimage_caption_field(document, container=folder)

    def get_browser(self):
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
        browser.handleErrors = False
        return browser

    def check_leadimage_caption_field(self, obj, container):
        browser = self.get_browser()
        browser.open("{}/edit".format(obj.absolute_url()))
        content = browser.contents
        soup = BeautifulSoup(content)
        lead_image_caption_widget = soup.find(
            id="form-widgets-ILeadImageBehavior-image_caption"
        )
        self.assertIsNotNone(lead_image_caption_widget)
        self.assertEqual(len(lead_image_caption_widget), 0)
        self.assertEqual(lead_image_caption_widget["type"], "hidden")

        browser.open("{}/++add++{}".format(container.absolute_url(), obj.portal_type))
        content = browser.contents
        soup = BeautifulSoup(content)
        lead_image_caption_widget = soup.find(
            id="form-widgets-ILeadImageBehavior-image_caption"
        )
        self.assertIsNotNone(lead_image_caption_widget)
        self.assertEqual(len(lead_image_caption_widget), 0)
        self.assertEqual(lead_image_caption_widget["type"], "hidden")

    def test_save_and_publish_on_edit_form(self):
        document = api.content.create(
            container=self.portal, type="Document", title="Document"
        )
        browser = self.get_browser()
        browser.open("{}/edit".format(document.absolute_url()))
        browser.getControl(name="form.buttons.save_and_publish").click()
        transaction.begin()
        self.assertEqual(api.content.get_state(document), "published")

    def test_save_and_publish_on_add_form(self):
        browser = self.get_browser()
        browser.open("{}/++add++Document".format(self.portal.absolute_url()))
        browser.getControl(name="form.widgets.IDublinCore.title").value = "New document"
        browser.getControl(name="form.buttons.save_and_publish").click()
        transaction.begin()
        self.assertEqual(
            api.content.get_state(self.portal["new-document"]), "published"
        )

    def test_save_and_publish_hidden_without_the_behavior(self):
        folder = api.content.create(
            container=self.portal, type="Folder", title="Folder"
        )
        browser = self.get_browser()
        browser.open("{}/edit".format(folder.absolute_url()))
        self.assertNotIn("form.buttons.save_and_publish", browser.contents)
        browser.open("{}/++add++Folder".format(self.portal.absolute_url()))
        self.assertNotIn("form.buttons.save_and_publish", browser.contents)

    def test_save_and_publish_hidden_without_publish_permission(self):
        document = api.content.create(
            container=self.portal, type="Document", title="Document"
        )
        # An editor may add and modify content, but not publish it.
        setRoles(self.portal, TEST_USER_ID, ["Contributor", "Editor"])
        browser = self.get_browser()
        browser.open("{}/edit".format(document.absolute_url()))
        self.assertNotIn("form.buttons.save_and_publish", browser.contents)
        browser.open("{}/++add++Document".format(self.portal.absolute_url()))
        self.assertNotIn("form.buttons.save_and_publish", browser.contents)
        # Saving is unaffected: the content is created, stays private, and the
        # editor is told nothing about publication.
        browser.getControl(name="form.widgets.IDublinCore.title").value = "New document"
        browser.getControl(name="form.buttons.save").click()
        transaction.begin()
        self.assertEqual(api.content.get_state(self.portal["new-document"]), "private")
        self.assertNotIn("could not be published", browser.contents)

    def test_save_and_publish_hidden_when_already_published(self):
        document = api.content.create(
            container=self.portal, type="Document", title="Document"
        )
        api.content.transition(obj=document, transition="publish")
        browser = self.get_browser()
        browser.open("{}/edit".format(document.absolute_url()))
        self.assertNotIn("form.buttons.save_and_publish", browser.contents)

    def test_save_and_publish_sits_next_to_save(self):
        document = api.content.create(
            container=self.portal, type="Document", title="Document"
        )
        browser = self.get_browser()
        for url in (
            "{}/edit".format(document.absolute_url()),
            "{}/++add++Document".format(self.portal.absolute_url()),
        ):
            browser.open(url)
            soup = BeautifulSoup(browser.contents)
            names = [
                node["name"] for node in soup.select("div.formControls button[name]")
            ]
            self.assertEqual(
                names,
                [
                    "form.buttons.save",
                    "form.buttons.save_and_publish",
                    "form.buttons.cancel",
                ],
            )

    def test_save_and_publish_does_not_publish_an_invalid_edit_form(self):
        document = api.content.create(
            container=self.portal, type="Document", title="Document"
        )
        browser = self.get_browser()
        browser.open("{}/edit".format(document.absolute_url()))
        browser.getControl(name="form.widgets.IDublinCore.title").value = ""
        browser.getControl(name="form.buttons.save_and_publish").click()
        transaction.begin()
        self.assertIn("Required input is missing", browser.contents)
        self.assertEqual(api.content.get_state(document), "private")

    def test_save_and_publish_does_not_publish_an_invalid_add_form(self):
        browser = self.get_browser()
        browser.open("{}/++add++Document".format(self.portal.absolute_url()))
        # The title is required: nothing is created, nothing is published.
        browser.getControl(name="form.buttons.save_and_publish").click()
        transaction.begin()
        self.assertIn("Required input is missing", browser.contents)
        self.assertEqual(len(api.content.find(portal_type="Document")), 0)


# <audit>
#   <file>test_forms.py</file>
#   <requirements_applied>R1, R2, R4, R5, R6</requirements_applied>
#   <deviations>
#     The design doc named a single test_save_and_publish.py. R5 (one test file
#     per production file) puts the button tests here, next to the rest of
#     browser/forms.py, and the helper tests in test_publish.py.
#     get_browser() was extracted from check_leadimage_caption_field (R4: shared
#     by several methods of this single class, so a method, not a base class).
#   </deviations>
#   <questions>None</questions>
# </audit>
