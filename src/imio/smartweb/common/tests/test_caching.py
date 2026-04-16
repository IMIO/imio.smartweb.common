# -*- coding: utf-8 -*-

from imio.smartweb.common.caching import ban_physicalpath
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import os
import unittest


class TestBanPhysicalpath(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def _make_request(self, x_forwarded_host="", http_host=""):
        return {
            "X-Forwarded-Host": x_forwarded_host,
            "HTTP_HOST": http_host,
        }

    def _make_portal(self, path=("", "Plone")):
        portal = Mock()
        portal.getPhysicalPath.return_value = path
        return portal

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_no_ban_when_caching_servers_not_set(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        env = {k: v for k, v in os.environ.items() if k != "CACHING_SERVERS"}
        with patch.dict(os.environ, env, clear=True):
            ban_physicalpath(
                self._make_request(http_host="www.example.com"), ("", "Plone", "en")
            )
        mock_request.assert_not_called()

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_no_ban_when_caching_servers_is_empty_string(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": ""}):
            ban_physicalpath(
                self._make_request(http_host="www.example.com"), ("", "Plone", "en")
            )
        mock_request.assert_not_called()

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_uses_x_forwarded_host_as_host_header(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        request = self._make_request(
            x_forwarded_host="www.example.com", http_host="internal.host"
        )
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(request, ("", "Plone", "en"))
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Host"], "www.example.com")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_falls_back_to_http_host_when_x_forwarded_host_missing(
        self, mock_portal_get, mock_request
    ):
        # Direct Varnish → Plone topology: X-Forwarded-Host is never set,
        # the browser's Host header lands in HTTP_HOST.
        mock_portal_get.return_value = self._make_portal()
        request = self._make_request(x_forwarded_host="", http_host="www.example.com")
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(request, ("", "Plone", "en"))
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Host"], "www.example.com")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_empty_host_header_when_both_host_headers_missing(
        self, mock_portal_get, mock_request
    ):
        mock_portal_get.return_value = self._make_portal()
        request = self._make_request(x_forwarded_host="", http_host="")
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(request, ("", "Plone", "en"))
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["headers"]["Host"], "")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_ban_method_is_used(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": "192.168.1.10"}):
            ban_physicalpath(
                self._make_request(http_host="www.example.com"), ("", "Plone", "en")
            )
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
                self._make_request(http_host="www.example.com"),
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
            ban_physicalpath(
                self._make_request(http_host="www.example.com"),
                ("", "Plone"),
            )
        args, _ = mock_request.call_args
        self.assertEqual(args[1], "http://192.168.1.10")

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_ban_sent_to_each_caching_server(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": "10.0.0.1 10.0.0.2"}):
            ban_physicalpath(
                self._make_request(http_host="www.example.com"),
                ("", "Plone", "en"),
            )
        self.assertEqual(mock_request.call_count, 2)
        urls = [c[0][1] for c in mock_request.call_args_list]
        self.assertIn("http://10.0.0.1/en", urls)
        self.assertIn("http://10.0.0.2/en", urls)

    @patch("imio.smartweb.common.caching.requests.request")
    @patch("imio.smartweb.common.caching.api.portal.get")
    def test_all_servers_receive_same_host_header(self, mock_portal_get, mock_request):
        mock_portal_get.return_value = self._make_portal()
        with patch.dict(os.environ, {"CACHING_SERVERS": "10.0.0.1 10.0.0.2"}):
            ban_physicalpath(
                self._make_request(http_host="www.example.com"),
                ("", "Plone", "en"),
            )
        for c in mock_request.call_args_list:
            self.assertEqual(c[1]["headers"]["Host"], "www.example.com")
