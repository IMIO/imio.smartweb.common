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
            return_value="secret-key",
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

    @patch("requests.post")
    def test_odwb_send_by_batches_returns_summary(self, mock_post):
        mock_post.side_effect = [
            MagicMock(status_code=200, text=""),
            MagicMock(status_code=400, text="bad item"),
        ]
        items = (item for item in [{"id": 1}, {"id": 2}, {"id": 3}])
        summary = self.endpoint.odwb_send(items, action="delete", batch_size=2)
        self.assertEqual(
            summary,
            {
                "service": "staging-service",
                "total": 3,
                "sent": 2,
                "batches": [
                    {"size": 2, "status_code": 200, "response": ""},
                    {"size": 1, "status_code": 400, "response": "bad item"},
                ],
            },
        )
        self.assertEqual(
            mock_post.call_args.args[0],
            "https://www.odwb.be/api/push/1.0/staging-service/temps_reel/delete/?pushkey=secret-key",
        )
        self.assertEqual(mock_post.call_args.kwargs["data"], '[{"id": 3}]')

    @patch("imio.smartweb.common.rest.odwb.is_log_active", return_value=True)
    @patch("requests.post")
    def test_odwb_send_hides_pushkey_in_logs(self, mock_post, mock_log_active):
        mock_post.return_value = MagicMock(status_code=200, text="")
        with self.assertLogs("imio.smartweb.common", level="INFO") as logs:
            self.endpoint.odwb_send([{"id": 1}])
        self.assertNotIn("secret-key", "\n".join(logs.output))
        self.assertTrue(any("?pushkey=***" in line for line in logs.output))

    @patch("requests.post")
    def test_odwb_post_hides_pushkey_in_error_logs(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Max retries exceeded with url: /api/push/1.0/?pushkey=secret-key"
        )
        with self.assertLogs("imio.smartweb.common", level="ERROR") as logs:
            self.endpoint.odwb_post("https://odwb/push?pushkey=secret-key", "[]")
        self.assertNotIn("secret-key", "\n".join(logs.output))
        self.assertIn("?pushkey=***", logs.output[0])

    @patch("requests.post")
    def test_odwb_send_without_items(self, mock_post):
        self.assertEqual(
            self.endpoint.odwb_send([]),
            {"service": "staging-service", "total": 0, "sent": 0, "batches": []},
        )
        mock_post.assert_not_called()
