# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING
from imio.smartweb.common.rest.utils import batch_results
from imio.smartweb.common.rest.utils import get_json
from imio.smartweb.common.rest.utils import hash_md5
from unittest.mock import patch
from unittest.mock import Mock

import json
import requests
import unittest


class TestRestUtils(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_ACCEPTANCE_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.url = "https://api.kamoulox.test/endpoint"

    @patch("imio.smartweb.common.rest.utils.requests.get")
    def test_get_json_success(self, mock_get):
        payload = {"ok": True, "items": [1, 2]}
        mock_get.return_value = Mock(status_code=200, text=json.dumps(payload))
        result = get_json(self.url)
        self.assertEqual(result, payload)
        mock_get.assert_called_once()
        (called_url,) = mock_get.call_args[0]
        self.assertEqual(called_url, self.url)
        kwargs = mock_get.call_args.kwargs
        self.assertEqual(kwargs["timeout"], 5)
        self.assertEqual(kwargs["headers"]["Accept"], "application/json")
        self.assertNotIn("Authorization", kwargs["headers"])

    @patch("imio.smartweb.common.rest.utils.requests.get")
    def test_get_json_non_200_returns_none(self, mock_get):
        mock_get.return_value = Mock(status_code=404, text="Not found")
        result = get_json(self.url)
        self.assertIsNone(result)

    @patch("imio.smartweb.common.rest.utils.logger")
    @patch("imio.smartweb.common.rest.utils.requests.get")
    def test_get_json_timeout_returns_none_and_logs(self, mock_get, mock_logger):
        mock_get.side_effect = requests.exceptions.Timeout()
        result = get_json(self.url)
        self.assertIsNone(result)
        mock_logger.warning.assert_called_once()
        # check if url is in log
        self.assertIn(self.url, mock_logger.warning.call_args[0][0])

    @patch("imio.smartweb.common.rest.utils.requests.get")
    def test_get_json_other_exception_returns_none(self, mock_get):
        mock_get.side_effect = RuntimeError("kamoulox")
        result = get_json(self.url)
        self.assertIsNone(result)

    @patch("imio.smartweb.common.rest.utils.requests.get")
    def test_get_json_sets_auth_header_when_provided(self, mock_get):
        mock_get.return_value = Mock(status_code=200, text="{}")
        auth = "Bearer TOKEN123"
        _ = get_json(self.url, auth=auth, timeout=10)
        mock_get.assert_called_once()
        kwargs = mock_get.call_args.kwargs
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["headers"]["Authorization"], auth)
        self.assertEqual(kwargs["headers"]["Accept"], "application/json")

    @patch("imio.smartweb.common.rest.utils.requests.get")
    def test_get_json_custom_timeout_is_used(self, mock_get):
        mock_get.return_value = Mock(status_code=200, text="{}")
        _ = get_json(self.url, timeout=2.5)
        self.assertEqual(mock_get.call_args.kwargs["timeout"], 2.5)

    def test_batch_results_exact_division(self):
        data = [1, 2, 3, 4]
        result = batch_results(data, 2)
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_batch_results_not_exact(self):
        data = [1, 2, 3, 4, 5]
        result = batch_results(data, 2)
        self.assertEqual(result, [[1, 2], [3, 4], [5]])

    def test_batch_results_batch_size_larger_than_list(self):
        data = [1, 2, 3]
        result = batch_results(data, 10)
        self.assertEqual(result, [[1, 2, 3]])

    def test_batch_results_empty_iterable(self):
        data = []
        result = batch_results(data, 3)
        self.assertEqual(result, [])

    def test_batch_results_with_generator(self):
        gen = (i for i in range(5))
        result = batch_results(gen, 2)
        self.assertEqual(result, [[0, 1], [2, 3], [4]])

    def test_hash_md5_basic_string(self):
        result = hash_md5("hello")
        self.assertEqual(result, "5d41402abc4b2a76b9719d911017c592")

    def test_hash_md5_empty_string(self):
        result = hash_md5("")
        self.assertEqual(result, "d41d8cd98f00b204e9800998ecf8427e")

    def test_hash_md5_unicode_string(self):
        result = hash_md5("éèà")
        # tu peux vérifier avec hashlib directement
        import hashlib

        expected = hashlib.md5("éèà".encode()).hexdigest()
        self.assertEqual(result, expected)
