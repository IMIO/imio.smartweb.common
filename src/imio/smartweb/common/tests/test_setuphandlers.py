# -*- coding: utf-8 -*-

from imio.smartweb.common.setuphandlers import set_omnia_core_settings
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest.mock import patch

import os
import unittest


class TestSetOmniaCoreSettings(unittest.TestCase):
    """Pre-fill imio.omnia.core control panel fields from the legacy
    application_id / PROJECT_ID environment variables."""

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    @patch("imio.omnia.core.settings.set_organization_id")
    @patch("imio.omnia.core.settings.set_application_id")
    @patch("imio.omnia.core.settings.get_organization_id", return_value="")
    @patch("imio.omnia.core.settings.get_application_id", return_value="")
    def test_sets_values_from_env_when_empty(
        self, m_get_app, m_get_org, m_set_app, m_set_org
    ):
        with patch.dict(os.environ, {"application_id": "myApp", "PROJECT_ID": "myOrg"}):
            set_omnia_core_settings()
        m_set_app.assert_called_once_with("myApp")
        m_set_org.assert_called_once_with("myOrg")

    @patch("imio.omnia.core.settings.set_organization_id")
    @patch("imio.omnia.core.settings.set_application_id")
    @patch("imio.omnia.core.settings.get_organization_id", return_value="")
    @patch("imio.omnia.core.settings.get_application_id", return_value="")
    def test_uses_defaults_when_env_absent(
        self, m_get_app, m_get_org, m_set_app, m_set_org
    ):
        with patch.dict(os.environ, {}, clear=True):
            set_omnia_core_settings()
        m_set_app.assert_called_once_with("iA.Smartweb")
        m_set_org.assert_called_once_with("smartweb")

    @patch("imio.omnia.core.settings.set_organization_id")
    @patch("imio.omnia.core.settings.set_application_id")
    @patch("imio.omnia.core.settings.get_organization_id", return_value="existingOrg")
    @patch("imio.omnia.core.settings.get_application_id", return_value="existingApp")
    def test_does_not_override_existing_values(
        self, m_get_app, m_get_org, m_set_app, m_set_org
    ):
        set_omnia_core_settings()
        m_set_app.assert_not_called()
        m_set_org.assert_not_called()


class TestSetOmniaCoreSettingsIntegration(unittest.TestCase):
    """Regression test against the *real* registry: the imio.omnia.core
    IOmniaCoreSettings records must exist after install so that
    set_omnia_core_settings() can actually write application_id /
    organization_id (the mocked unit tests above can't catch a missing
    registry record)."""

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def test_prefill_writes_to_real_registry(self):
        from imio.omnia.core.settings import get_application_id
        from imio.omnia.core.settings import get_organization_id
        from imio.omnia.core.settings import set_application_id
        from imio.omnia.core.settings import set_organization_id

        # Start from an empty state (also proves the records exist).
        set_application_id("")
        set_organization_id("")
        with patch.dict(os.environ, {"application_id": "myApp", "PROJECT_ID": "myOrg"}):
            set_omnia_core_settings()
        self.assertEqual(get_application_id(), "myApp")
        self.assertEqual(get_organization_id(), "myOrg")
