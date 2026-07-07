# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.privacy.utils import get_all_consent_reasons
from types import SimpleNamespace

import unittest


def make_reason(name, lawful_basis):
    return SimpleNamespace(
        __name__=name, lawful_basis=SimpleNamespace(__name__=lawful_basis)
    )


class FakePrivacyTool:
    def __init__(self, reasons):
        self._reasons = reasons

    def getAllReasons(self):
        return self._reasons


class TestGetAllConsentReasons(unittest.TestCase):
    def test_keeps_only_consent_reasons(self):
        consent_a = make_reason("analytics", "consent")
        consent_b = make_reason("embed", "consent")
        legitimate = make_reason("basic", "legitimate_interest")
        tool = FakePrivacyTool(
            {"analytics": consent_a, "embed": consent_b, "basic": legitimate}
        )

        result = list(get_all_consent_reasons(tool))

        self.assertEqual(result, [consent_a, consent_b])
        self.assertNotIn(legitimate, result)

    def test_empty_when_no_consent_reason(self):
        tool = FakePrivacyTool({"basic": make_reason("basic", "legitimate_interest")})
        self.assertEqual(list(get_all_consent_reasons(tool)), [])

    def test_empty_when_no_reason_at_all(self):
        self.assertEqual(list(get_all_consent_reasons(FakePrivacyTool({}))), [])
