# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.vocabularies.types import BAD_TYPES
from plone.uuid.interfaces import IUUID
from zope.component import queryMultiAdapter

import unittest


class TestDescription(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_description(self):
        portal_types = api.portal.get_tool("portal_types")
        bad_types = BAD_TYPES + ["Discussion Item"]
        all_types = [t for t in portal_types.listContentTypes() if t not in bad_types]
        for pt in all_types:
            content_type = api.content.create(
                title="My {}".format(pt), container=self.portal, type=pt
            )
            content_type.description = (
                "My bold **description** is wonderfull with \r\n carriage return \r\n"
            )
            view = queryMultiAdapter((content_type, self.request), name="description")
            self.assertEqual(
                view.description(),
                "My bold <strong>description</strong> is wonderfull with <br/> carriage return <br/>",
            )
            content_type.reindexObject()

            uuid = IUUID(content_type)
            brain = api.content.find(UID=uuid)[0]
            catalog = api.portal.get_tool("portal_catalog")
            indexes = catalog.getIndexDataForRID(brain.getRID())
            self.assertEqual(
                indexes.get("Description"),
                [
                    "my",
                    "bold",
                    "description",
                    "is",
                    "wonderfull",
                    "with",
                    "carriage",
                    "return",
                ],
            )

            content_type.description = "My bold **description** is wonderfull with ** \r\n carriage return \r\n"
            view = queryMultiAdapter((content_type, self.request), name="description")
            self.assertEqual(
                view.description(),
                "My bold <strong>description</strong> is wonderfull with ** <br/> carriage return <br/>",
            )
