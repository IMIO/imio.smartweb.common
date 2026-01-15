# -*- coding: utf-8 -*-
# imio/smartweb/core/browser/categorization_button_edit.py
from imio.smartweb.common.config import APPLICATION_ID
from imio.smartweb.common.config import PROJECT_ID
from z3c.form import widget as z3c_widget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

FIELD_NAME = "categorization_ia_link"  # Internal id for dummy field


class EditHtmlSnippetWidget(z3c_widget.Widget):
    """Widget HTML (bouton + JS) avec template ZPT."""

    template = ViewPageTemplateFile("html_snippet_widget.pt")
    x_imio_application = APPLICATION_ID
    x_imio_municipality = PROJECT_ID

    def update(self):
        # edit : context == objet
        base = self.context.absolute_url()
        self.endpoint = f"{base}/@@ProcessCategorizeContent"
        # Unique id for button + status zone
        self.wid = getattr(self, "name", FIELD_NAME)

        # Désactiver le bouton si aucune section texte avec contenu n'est présente
        self.klass = getattr(self, "klass", "")
        has_text_content = False

        # Vérifie si le contexte contient au moins une section texte avec du contenu
        try:
            for item in getattr(self.context, "objectItems", lambda: [])():
                obj = item[1]
                # Vérifier si la section texte a du contenu (non vide)
                text_output = getattr(getattr(obj, "text", None), "output", "")
                if text_output and text_output.strip():
                    has_text_content = True
                    break
        except Exception:
            pass

        if not has_text_content:
            self.klass = f"{self.klass} disabled".strip() if self.klass else "disabled"
            self.is_disabled = True
        else:
            self.is_disabled = False

    def render(self):
        return self.template()


class AddHtmlSnippetWidget(z3c_widget.Widget):
    template = ViewPageTemplateFile("html_snippet_widget.pt")
    x_imio_application = APPLICATION_ID
    x_imio_municipality = PROJECT_ID

    def update(self):
        # ++add++ : context = container ; edit : context = object
        base = self.context.absolute_url()
        self.endpoint = f"{base}/@@ProcessCategorizeContent"
        self.wid = getattr(self, "name", "categorization_ia_link")
        self.klass = getattr(self, "klass", "")
        self.is_disabled = False

    def render(self):
        return self.template()
