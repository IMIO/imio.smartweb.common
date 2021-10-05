# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE


class CustomAddForm(DefaultAddForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False

    def updateFields(self):
        super(CustomAddForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE

    def updateWidgets(self):
        super(CustomAddForm, self).updateWidgets()
        if "IBasic.description" in self.widgets:
            self.widgets["IBasic.description"].description = _(
                u"Use **text** to set text in bold."
            )
        elif "IDublinCore.description" in self.widgets:
            self.widgets["IDublinCore.description"].description = _(
                u"Use **text** to set text in bold."
            )


class CustomAddView(DefaultAddView):
    form = CustomAddForm


class CustomEditForm(DefaultEditForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False

    def updateFields(self):
        super(CustomEditForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE

    def updateWidgets(self):
        super(CustomEditForm, self).updateWidgets()
        if "IBasic.description" in self.widgets:
            self.widgets["IBasic.description"].description = _(
                u"Use **text** to set text in bold."
            )
        elif "IDublinCore.description" in self.widgets:
            self.widgets["IDublinCore.description"].description = _(
                u"Use **text** to set text in bold."
            )


CustomEditView = layout.wrap_form(CustomEditForm)
