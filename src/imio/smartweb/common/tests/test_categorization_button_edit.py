# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.forms import CustomEditForm
from imio.smartweb.common.ia.browser.categorization_button_edit import FIELD_NAME
from imio.smartweb.common.ia.browser.categorization_button_edit import (
    IACategorizeEditForm,
)
from imio.smartweb.common.ia.widgets.html_snippet_widget import EditHtmlSnippetWidget
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from types import SimpleNamespace
from unittest.mock import patch
from z3c.form.interfaces import DISPLAY_MODE

import unittest

PREFIXED_KEY = f"form.widgets.{FIELD_NAME}"


class FakeWidgets(dict):
    """A dict-like widgets manager that is truthy even when empty, mirroring the
    real z3c.form Manager (which has no `_widgets` attribute -> fallback path)."""

    def __bool__(self):
        return True


class DataKeysManager:
    """A widgets manager exposing both `_data_keys` and `_widgets` (the compat
    shape the edit form handles specially)."""

    def __init__(self, keys=None, widgets=None):
        self._data_keys = list(keys or [])
        self._widgets = list(widgets or [])

    def keys(self):
        return list(self._data_keys)

    def __bool__(self):
        return True


def make_group(name, widgets):
    return SimpleNamespace(**{"__name__": name, "widgets": widgets})


class TestIACategorizeEditForm(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def _make_form(self, groups):
        form = IACategorizeEditForm.__new__(IACategorizeEditForm)
        form.context = self.portal
        form.request = self.request
        form.groups = groups
        return form

    def _update(self, form):
        with patch.object(CustomEditForm, "update"):
            form.update()

    # ---- early returns -------------------------------------------------
    def test_returns_when_no_groups(self):
        form = self._make_form([])
        self._update(form)  # must not raise

    def test_returns_when_no_categorization_group(self):
        form = self._make_form([make_group("layout", FakeWidgets())])
        self._update(form)  # must not raise

    def test_returns_when_categorization_has_no_widgets(self):
        form = self._make_form([make_group("categorization", None)])
        self._update(form)  # must not raise

    def test_returns_when_button_already_present(self):
        widgets = FakeWidgets({PREFIXED_KEY: object()})
        form = self._make_form([make_group("categorization", widgets)])
        self._update(form)
        # Unchanged: the dedup guard returned before rebuilding.
        self.assertEqual(list(widgets), [PREFIXED_KEY])

    # ---- _data_keys / _widgets manager --------------------------------
    def test_data_keys_manager_inserts_at_top(self):
        mgr = DataKeysManager(keys=["form.widgets.other"], widgets=["OTHER"])
        form = self._make_form([make_group("categorization", mgr)])
        self._update(form)
        self.assertEqual(mgr._data_keys[0], PREFIXED_KEY)
        self.assertEqual(mgr._data_keys[1], "form.widgets.other")
        self.assertEqual(mgr._widgets[0].mode, DISPLAY_MODE)
        self.assertIsInstance(mgr._widgets[0], EditHtmlSnippetWidget)

    def test_data_keys_manager_removes_residual(self):
        # keys() hides the residual so the dedup guard passes; the residual is
        # then stripped from _data_keys/_widgets before re-inserting.
        class Tricky(DataKeysManager):
            def keys(self):
                return []

        mgr = Tricky(keys=[PREFIXED_KEY], widgets=["OLD"])
        form = self._make_form([make_group("categorization", mgr)])
        self._update(form)
        self.assertEqual(mgr._data_keys, [PREFIXED_KEY])
        self.assertEqual(len(mgr._widgets), 1)
        self.assertIsInstance(mgr._widgets[0], EditHtmlSnippetWidget)

    def test_data_keys_manager_tolerates_pop_error(self):
        class RaisingList(list):
            def pop(self, *args):
                raise RuntimeError("boom")

        class PopErrorManager(DataKeysManager):
            def keys(self):
                return []

        mgr = PopErrorManager(keys=[PREFIXED_KEY])
        mgr._widgets = RaisingList(["OLD"])
        form = self._make_form([make_group("categorization", mgr)])
        self._update(form)  # the pop error is swallowed
        self.assertEqual(mgr._data_keys[0], PREFIXED_KEY)

    # ---- fallback (plain mapping manager) -----------------------------
    def test_fallback_rebuilds_mapping_with_button_first(self):
        widgets = FakeWidgets({"other": "OTHER"})
        form = self._make_form([make_group("categorization", widgets)])
        self._update(form)
        self.assertIn(PREFIXED_KEY, widgets)
        self.assertEqual(widgets[PREFIXED_KEY].mode, DISPLAY_MODE)
        self.assertEqual(widgets["other"], "OTHER")

    def test_fallback_tolerates_clear_error(self):
        class ClearRaises(FakeWidgets):
            def clear(self):
                raise RuntimeError("boom")

        widgets = ClearRaises({"other": "OTHER"})
        form = self._make_form([make_group("categorization", widgets)])
        self._update(form)
        self.assertIn(PREFIXED_KEY, widgets)

    def test_fallback_last_resort_when_setitem_raises(self):
        class SetItemRaises(FakeWidgets):
            def __setitem__(self, key, value):
                raise RuntimeError("boom")

        widgets = SetItemRaises()
        form = self._make_form([make_group("categorization", widgets)])
        self._update(form)  # every insertion raises but is swallowed
        self.assertNotIn(PREFIXED_KEY, widgets)
