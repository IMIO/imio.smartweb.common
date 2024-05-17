# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone import api
from plone.testing import z2

import imio.smartweb.common
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import unittest


class ImioSmartwebCommonLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=imio.smartweb.common, name="testing.zcml")

    def setUpPloneSite(self, portal):
        api.user.create(email="test@imio.be", username="test")
        applyProfile(portal, "imio.smartweb.common:testing")


IMIO_SMARTWEB_COMMON_FIXTURE = ImioSmartwebCommonLayer()


IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_SMARTWEB_COMMON_FIXTURE,),
    name="ImioSmartwebCommonLayer:IntegrationTesting",
)


IMIO_SMARTWEB_COMMON_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_SMARTWEB_COMMON_FIXTURE,),
    name="ImioSmartwebCommonLayer:FunctionalTesting",
)


IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_SMARTWEB_COMMON_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioSmartwebCommonLayer:AcceptanceTesting",
)


class ImioSmartwebCommonTestCase(unittest.TestCase):
    def assertVocabularyLen(self, vocname, voc_len):
        factory = getUtility(IVocabularyFactory, vocname)
        vocabulary = factory()
        self.assertEqual(len(vocabulary), voc_len)
