# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.forms import CustomAddForm
from imio.smartweb.common.ia.browser.categorization_button_add import FIELD_NAME
from imio.smartweb.common.ia.browser.categorization_button_add import (
    IACategorizeAddForm,
)
from imio.smartweb.common.ia.browser.categorization_button_add import (
    IACategorizeAddView,
)
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone.dexterity.browser.add import DefaultAddView
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import HIDDEN_MODE

import unittest


PREFIXED_KEY = f"form.widgets.{FIELD_NAME}"


class FakeWidgets(dict):
    """A z3c.form widgets manager stand-in: dict-like but always truthy, so an
    empty group still passes the `not cat.widgets` guard (as the real manager
    does)."""

    def __bool__(self):
        return True


def make_group(name, widgets):
    return SimpleNamespace(**{"__name__": name, "widgets": widgets})


class TestIACategorizeAddView(unittest.TestCase):
    def test_form_wiring(self):
        # The view only wires the custom form onto the default add view.
        self.assertTrue(issubclass(IACategorizeAddView, DefaultAddView))
        self.assertIs(IACategorizeAddView.form, IACategorizeAddForm)


class TestIACategorizeAddForm(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def _make_form(self, groups):
        # Build the form without running the heavy Dexterity __init__; we only
        # exercise update(), whose super() call is stubbed so we fully control
        # self.groups. The context/request stay real (the injected widget uses
        # context.absolute_url()).
        form = IACategorizeAddForm.__new__(IACategorizeAddForm)
        form.context = self.portal
        form.request = self.request
        form.groups = groups
        return form

    def _update(self, form):
        with patch.object(CustomAddForm, "update"):
            form.update()

    def test_hides_title_and_injects_button(self):
        hide_title = SimpleNamespace(mode=None, value=None)
        layout = make_group("layout", {"hide_title": hide_title})
        cat_widgets = FakeWidgets()
        categorization = make_group("categorization", cat_widgets)
        form = self._make_form([layout, categorization])

        self._update(form)

        # hide_title forced hidden + preselected
        self.assertEqual(hide_title.mode, HIDDEN_MODE)
        self.assertEqual(hide_title.value, ["selected"])
        # HTML snippet widget injected in the categorization group, in display mode
        self.assertIn(PREFIXED_KEY, cat_widgets)
        self.assertEqual(cat_widgets[PREFIXED_KEY].mode, DISPLAY_MODE)

    def test_returns_early_if_button_already_present(self):
        cat_widgets = FakeWidgets({FIELD_NAME: object()})
        categorization = make_group("categorization", cat_widgets)
        form = self._make_form([categorization])

        self._update(form)

        # No second (prefixed) widget added: the dedup guard returned early.
        self.assertNotIn(PREFIXED_KEY, cat_widgets)
        self.assertEqual(list(cat_widgets), [FIELD_NAME])

    def test_no_categorization_group_returns(self):
        # A layout group without a hide_title widget exercises the false branch
        # of the "hide_title in widgets" test; absence of a categorization group
        # makes update() return before injecting anything.
        layout = make_group("layout", {})
        form = self._make_form([layout])

        self._update(form)  # must not raise

    def test_categorization_without_widgets_returns(self):
        categorization = make_group("categorization", None)
        form = self._make_form([categorization])

        self._update(form)  # must not raise

    def test_updates_groups_when_empty(self):
        cat_widgets = FakeWidgets()
        categorization = make_group("categorization", cat_widgets)
        form = self._make_form([])
        # Empty groups -> updateGroups() is invoked; simulate it populating.
        form.updateGroups = MagicMock(
            side_effect=lambda: setattr(form, "groups", [categorization])
        )

        self._update(form)

        form.updateGroups.assert_called_once()
        self.assertIn(PREFIXED_KEY, cat_widgets)

    def test_fallback_to_short_key_when_prefixed_key_raises(self):
        class RaiseOnPrefixed(FakeWidgets):
            def __setitem__(self, key, value):
                if key.startswith("form.widgets."):
                    raise KeyError(key)
                super().__setitem__(key, value)

        cat_widgets = RaiseOnPrefixed()
        categorization = make_group("categorization", cat_widgets)
        form = self._make_form([categorization])

        self._update(form)

        self.assertIn(FIELD_NAME, cat_widgets)
        self.assertNotIn(PREFIXED_KEY, cat_widgets)

    def test_low_level_fallback_when_all_assignments_raise(self):
        class RaiseAlways(FakeWidgets):
            def __init__(self):
                super().__init__()
                self._data_keys = []
                self._widgets = []

            def __setitem__(self, key, value):
                raise KeyError(key)

        cat_widgets = RaiseAlways()
        categorization = make_group("categorization", cat_widgets)
        form = self._make_form([categorization])

        self._update(form)

        self.assertEqual(cat_widgets._data_keys, [FIELD_NAME])
        self.assertEqual(len(cat_widgets._widgets), 1)
