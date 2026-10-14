# -*- coding: utf-8 -*-

from imio.smartweb.common.rest.odwb import OdwbBaseEndpointGet
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from unittest.mock import MagicMock
from unittest.mock import patch

import requests
import unittest


class TestOdwbPost(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        with patch(
            "imio.smartweb.common.rest.odwb.api.portal.get_registry_record",
            return_value="pushkey",
        ):
            self.endpoint = OdwbBaseEndpointGet(
                self.portal, self.layer["request"], "staging-service", "key"
            )

    @patch("requests.post")
    def test_odwb_post_returns_status_code_and_response(self, mock_post):
        mock_post.return_value = MagicMock(status_code=400, text="bad pushkey")
        result = self.endpoint.odwb_post("https://odwb/push", "[]")
        self.assertEqual(result, {"status_code": 400, "response": "bad pushkey"})

    @patch("requests.post")
    def test_odwb_post_on_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("too slow")
        result = self.endpoint.odwb_post("https://odwb/push", "[]")
        self.assertEqual(
            result, {"status_code": None, "response": "ODWB : Request timed out"}
        )

    @patch("requests.post")
    def test_odwb_query_still_returns_text(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, text="")
        self.assertEqual(self.endpoint.odwb_query("https://odwb/push", "[]"), "")
