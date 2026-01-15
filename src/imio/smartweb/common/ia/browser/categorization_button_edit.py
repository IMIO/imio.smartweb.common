# -*- coding: utf-8 -*-
from imio.smartweb.common.browser.forms import CustomEditForm
from imio.smartweb.common.ia.widgets.html_snippet_widget import EditHtmlSnippetWidget
from plone.z3cform import layout
from zope import schema
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.widget import FieldWidget


FIELD_NAME = "categorization_ia_link"  # Internal id for dummy field


class IACategorizeEditForm(CustomEditForm):
    """Vue edit custom, avec bouton 'Catégoriser' injecté en haut de 'categorization'."""

    def update(self):
        super(IACategorizeEditForm, self).update()

        # Inject button on top of 'categorization' fieldset
        if not getattr(self, "groups", None):
            return

        # Find 'categorization' group
        cat = next(
            (g for g in self.groups if getattr(g, "__name__", "") == "categorization"),
            None,
        )
        if not cat or not getattr(cat, "widgets", None):
            return

        # Avoid doublons (refresh) if already here => stop
        existing_keys = list(getattr(cat.widgets, "keys", lambda: [])())
        for k in existing_keys:
            if (
                k.endswith(FIELD_NAME)
                or k == FIELD_NAME
                or k.endswith(f"form.widgets.{FIELD_NAME}")
            ):
                return

        # Create dummy field + FieldWidget(HtmlSnippetWidget)
        zfield = schema.Text(__name__=FIELD_NAME, title="", description="")
        w = FieldWidget(zfield, EditHtmlSnippetWidget(self.request))
        w.mode = DISPLAY_MODE
        w.context = self.context
        w.form = self
        w.ignoreContext = True
        w.label = ""
        w.update()  # prépare endpoint/wid

        key = f"form.widgets.{FIELD_NAME}"

        if hasattr(cat.widgets, "_data_keys") and hasattr(cat.widgets, "_widgets"):
            # Remove residual occurrences
            try:
                while key in cat.widgets._data_keys:
                    idx = cat.widgets._data_keys.index(key)
                    cat.widgets._data_keys.pop(idx)
                    cat.widgets._widgets.pop(idx)
            except Exception:
                pass
            cat.widgets._data_keys.insert(0, key)
            cat.widgets._widgets.insert(0, w)
            return

        # fallback : rebuild mapping with our with our widget
        try:
            existing = [(k, cat.widgets[k]) for k in list(cat.widgets.keys())]
            try:
                cat.widgets.clear()
            except Exception:
                pass
            # Firstly, our widget
            cat.widgets[key] = w
            # Next...
            for k, ww in existing:
                if k != key:
                    cat.widgets[k] = ww
        except Exception:
            # Last resort: If nothing else worked
            try:
                cat.widgets[key] = w
            except Exception:
                pass


IACategorizeEditView = layout.wrap_form(IACategorizeEditForm)
