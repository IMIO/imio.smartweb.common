# -*- coding: utf-8 -*-

from imio.smartweb.common.config import DESCRIPTION_MAX_LENGTH
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
        # Description field has a maximum number of chars
        if "IBasic.description" in self.fields:
            self.fields["IBasic.description"].field.max_length = DESCRIPTION_MAX_LENGTH
        elif "IDublinCore.description" in self.fields:
            self.fields[
                "IDublinCore.description"
            ].field.max_length = DESCRIPTION_MAX_LENGTH

    def updateWidgets(self):
        super(CustomAddForm, self).updateWidgets()
        # Change Description field help text
        if "IBasic.description" in self.widgets:
            self.widgets["IBasic.description"].description = _(
                u"Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={u"max": DESCRIPTION_MAX_LENGTH},
            )
        elif "IDublinCore.description" in self.widgets:
            self.widgets["IDublinCore.description"].description = _(
                u"Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={u"max": DESCRIPTION_MAX_LENGTH},
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
        # Description field has a maximum number of chars
        if "IBasic.description" in self.fields:
            self.fields["IBasic.description"].field.max_length = DESCRIPTION_MAX_LENGTH
        elif "IDublinCore.description" in self.fields:
            self.fields[
                "IDublinCore.description"
            ].field.max_length = DESCRIPTION_MAX_LENGTH

    def updateWidgets(self):
        super(CustomEditForm, self).updateWidgets()
        # Change Description field help text
        if "IBasic.description" in self.widgets:
            self.widgets["IBasic.description"].description = _(
                u"Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={u"max": DESCRIPTION_MAX_LENGTH},
            )
        elif "IDublinCore.description" in self.widgets:
            self.widgets["IDublinCore.description"].description = _(
                u"Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={u"max": DESCRIPTION_MAX_LENGTH},
            )


CustomEditView = layout.wrap_form(CustomEditForm)
