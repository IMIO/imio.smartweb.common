# -*- coding: utf-8 -*-

from imio.smartweb.common.sso import basic_auth_header
from imio.smartweb.common.sso import clear_sso_token_cache
from imio.smartweb.common.sso import get_sso_auth_header
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest.mock import Mock
from unittest.mock import patch

import base64
import json
import os
import requests
import time
import unittest

SSO_ENVIRON = {
    "SSO_APPS_CLIENT_ID": "imio-apps-events",
    "SSO_APPS_CLIENT_SECRET": "client-secret",
    "SSO_APPS_URL": "https://sso/token",
    "SSO_APPS_USER_USERNAME": "events-user",
    "SSO_APPS_USER_PASSWORD": "events-pwd",
}


def make_jwt(exp):
    def encode(data):
        raw = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        return raw.rstrip("=")

    return f"{encode({'alg': 'RS256'})}.{encode({'exp': exp})}.signature"


def token_response(token, status_code=200):
    return Mock(status_code=status_code, json=Mock(return_value={"id_token": token}))


@patch.dict(os.environ, SSO_ENVIRON)
@patch("imio.smartweb.common.sso.requests.post")
class TestSso(unittest.TestCase):

    def setUp(self):
        clear_sso_token_cache()

    def test_basic_auth_header(self, mock_post):
        self.assertEqual(basic_auth_header("u", "p"), "Basic dTpw")

    def test_get_sso_auth_header_bearer(self, mock_post):
        token = make_jwt(time.time() + 300)
        mock_post.return_value = token_response(token)
        self.assertEqual(get_sso_auth_header(), f"Bearer {token}")
        self.assertEqual(mock_post.call_args.args[0], "https://sso/token")
        self.assertEqual(mock_post.call_args.kwargs["timeout"], 10)
        payload = mock_post.call_args.kwargs["data"]
        self.assertEqual(payload["client_id"], "imio-apps-events")
        self.assertEqual(payload["username"], "events-user")

    def test_get_sso_auth_header_uses_cache(self, mock_post):
        mock_post.return_value = token_response(make_jwt(time.time() + 300))
        get_sso_auth_header()
        get_sso_auth_header()
        self.assertEqual(mock_post.call_count, 1)

    def test_get_sso_auth_header_expired_cache(self, mock_post):
        # expires before the margin: never reused
        mock_post.return_value = token_response(make_jwt(time.time() + 10))
        get_sso_auth_header()
        get_sso_auth_header()
        self.assertEqual(mock_post.call_count, 2)

    def test_get_sso_auth_header_no_exp(self, mock_post):
        mock_post.return_value = token_response("not-a-jwt")
        self.assertEqual(get_sso_auth_header(), "Bearer not-a-jwt")
        get_sso_auth_header()
        self.assertEqual(mock_post.call_count, 2)

    def test_get_sso_auth_header_cache_key(self, mock_post):
        mock_post.return_value = token_response(make_jwt(time.time() + 300))
        get_sso_auth_header()
        with patch.dict(os.environ, {"SSO_APPS_USER_USERNAME": "other-user"}):
            get_sso_auth_header()
        self.assertEqual(mock_post.call_count, 2)

    def test_get_sso_auth_header_no_config(self, mock_post):
        # no env basic auth fallback: each missing var gives no header
        for var in SSO_ENVIRON:
            with patch.dict(os.environ, {var: ""}):
                self.assertIsNone(get_sso_auth_header())
        mock_post.assert_not_called()

    def test_get_sso_auth_header_keycloak_errors(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        self.assertIsNone(get_sso_auth_header())
        mock_post.side_effect = None
        mock_post.return_value = Mock(status_code=401, json=Mock(return_value={}))
        self.assertIsNone(get_sso_auth_header())
        mock_post.return_value = Mock(
            status_code=502, json=Mock(side_effect=ValueError)
        )
        self.assertIsNone(get_sso_auth_header())

    def test_get_sso_auth_header_never_logs_secrets(self, mock_post):
        token = make_jwt(time.time() + 300)
        with self.assertLogs("imio.smartweb.common", level="INFO") as logs:
            mock_post.return_value = Mock(status_code=401, json=Mock(return_value={}))
            get_sso_auth_header()
            mock_post.side_effect = requests.exceptions.ConnectionError()
            get_sso_auth_header()
            with patch.dict(os.environ, {"SSO_APPS_URL": ""}):
                get_sso_auth_header()
            mock_post.side_effect = None
            mock_post.return_value = token_response(token)
            get_sso_auth_header()
        output = "\n".join(logs.output)
        for secret in ("client-secret", "events-pwd", token):
            self.assertNotIn(secret, output)


def set_setting(name, value):
    api.portal.set_registry_record(f"imio.smartweb.common.sso.{name}", value)


@patch.dict(os.environ, SSO_ENVIRON)
@patch("imio.smartweb.common.sso.requests.post")
class TestSsoBasicAuth(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        clear_sso_token_cache()

    def test_settings_registered(self, mock_post):
        self.assertFalse(
            api.portal.get_registry_record("imio.smartweb.common.sso.force_basic_auth")
        )
        self.assertIsNone(
            api.portal.get_registry_record(
                "imio.smartweb.common.sso.basic_auth_username"
            )
        )
        self.assertIsNone(
            api.portal.get_registry_record(
                "imio.smartweb.common.sso.basic_auth_password"
            )
        )

    def test_get_sso_auth_header_force_basic_auth(self, mock_post):
        set_setting("basic_auth_username", "agenda-user")
        set_setting("basic_auth_password", "agenda-pwd")
        # switch off: SSO token
        mock_post.return_value = token_response(make_jwt(time.time() + 300))
        self.assertTrue(get_sso_auth_header().startswith("Bearer "))
        # switch on: basic auth, Keycloak is not called
        mock_post.reset_mock()
        set_setting("force_basic_auth", True)
        self.assertEqual(
            get_sso_auth_header(), basic_auth_header("agenda-user", "agenda-pwd")
        )
        mock_post.assert_not_called()

    def test_get_sso_auth_header_force_basic_auth_without_credentials(self, mock_post):
        set_setting("force_basic_auth", True)
        set_setting("basic_auth_username", "agenda-user")
        with self.assertLogs("imio.smartweb.common", level="WARNING"):
            self.assertIsNone(get_sso_auth_header())
        mock_post.assert_not_called()

    def test_controlpanel_view(self, mock_post):
        view = api.content.get_view("sso-controlpanel", self.portal, self.request)
        self.assertIn("basic_auth_password", view())

    def test_controlpanel_keeps_password(self, mock_post):
        set_setting("basic_auth_password", "agenda-pwd")
        view = api.content.get_view("sso-controlpanel", self.portal, self.request)
        form = view.form_instance
        form.update()
        form.applyChanges(
            {
                "force_basic_auth": True,
                "basic_auth_username": "agenda-user",
                "basic_auth_password": None,
            }
        )
        self.assertEqual(
            api.portal.get_registry_record(
                "imio.smartweb.common.sso.basic_auth_password"
            ),
            "agenda-pwd",
        )
        self.assertTrue(
            api.portal.get_registry_record("imio.smartweb.common.sso.force_basic_auth")
        )

    def test_upgrade_1045_to_1046(self, mock_post):
        registry = api.portal.get_tool("portal_registry")
        names = ("force_basic_auth", "basic_auth_username", "basic_auth_password")
        for name in names:
            del registry.records[f"imio.smartweb.common.sso.{name}"]
        portal_setup = api.portal.get_tool("portal_setup")
        portal_setup.runAllImportStepsFromProfile(
            "profile-imio.smartweb.common.upgrades:upgrade_1045_to_1046"
        )
        for name in names:
            self.assertIn(f"imio.smartweb.common.sso.{name}", registry.records)
        controlpanel = api.portal.get_tool("portal_controlpanel")
        actions = [a.getId() for a in controlpanel.listActions()]
        self.assertIn("sso-controlpanel", actions)
