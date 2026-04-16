# -*- coding: utf-8 -*-

from imio.smartweb.common.caching import ban_physicalpath
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest.mock import Mock
from unittest.mock import patch

import os
import unittest


class TestBanPhysicalpath(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def _make_portal(self, path=("", "Plone"), absolute_url="http://www.kamoulox.be"):
        portal = Mock()
        portal.getPhysicalPath.return_value = path
        portal.absolute_url.return_value = absolute_url
        return portal

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_no_ban_when_caching_servers_not_set(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        env = {k: v for k, v in os.environ.items() if k != "CACHING_SERVERS"}
        with patch.dict(os.environ, env, clear=True):
            ban_physicalpath(None, ("", "Plone", "en"))
        mock_request.assert_not_called()

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_no_ban_when_caching_servers_is_empty_string(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": ""}):
            ban_physicalpath(None, ("", "Plone", "en"))
        mock_request.assert_not_called()

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_uses_website_hostname_env_var_as_host_header(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal(
            absolute_url="http://portal.internal.kamoulox.be"
        )
        with patch.dict(
            os.environ,
            {"CACHING_SERVERS": "192.168.1.10", "WEBSITE_HOSTNAME": "www.kamoulox.be"},
        ):
            ban_physicalpath(None, ("", "Plone", "en"))
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Host"], "www.kamoulox.be")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_falls_back_to_portal_absolute_url_when_website_hostname_not_set(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal(
            absolute_url="http://fallback.kamoulox.be"
        )
        env = {k: v for k, v in os.environ.items() if k != "WEBSITE_HOSTNAME"}
        with patch.dict(
            os.environ, {**env, "CACHING_SERVERS": "192.168.1.10"}, clear=True
        ):
            ban_physicalpath(None, ("", "Plone", "en"))
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Host"], "fallback.kamoulox.be")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_website_hostname_takes_precedence_over_portal_url(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal(
            absolute_url="http://portal.internal.kamoulox.be"
        )
        with patch.dict(
            os.environ,
            {
                "CACHING_SERVERS": "192.168.1.10",
                "WEBSITE_HOSTNAME": "override.kamoulox.be",
            },
        ):
            ban_physicalpath(None, ("", "Plone", "en"))
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Host"], "override.kamoulox.be")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_ban_method_is_used(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(None, ("", "Plone", "en"))
        args, _ = mock_request.call_args
        self.assertEqual(args[0], "BAN")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_ban_url_includes_path_relative_to_portal(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal(path=("", "Plone"))
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(
                None,
                ("", "Plone", "en", "home", "footer"),
            )
        args, _ = mock_request.call_args
        self.assertEqual(args[1], "http://192.168.1.10/en/home/footer")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_ban_url_is_server_root_when_banning_portal(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal(path=("", "Plone"))
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(None, ("", "Plone"))
        args, _ = mock_request.call_args
        self.assertEqual(args[1], "http://192.168.1.10")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_ban_sent_to_each_caching_server(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": "10.0.0.1 10.0.0.2"}):
            ban_physicalpath(None, ("", "Plone", "en"))
        self.assertEqual(mock_request.call_count, 2)
        urls = [c[0][1] for c in mock_request.call_args_list]
        self.assertIn("http://10.0.0.1/en", urls)
        self.assertIn("http://10.0.0.2/en", urls)

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_all_servers_receive_same_host_header(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(
            os.environ,
            {
                "CACHING_SERVERS": "10.0.0.1 10.0.0.2",
                "WEBSITE_HOSTNAME": "www.kamoulox.be",
            },
        ):
            ban_physicalpath(None, ("", "Plone", "en"))
        for c in mock_request.call_args_list:
            self.assertEqual(c[1]["headers"]["Host"], "www.kamoulox.be")
