# -*- coding: utf-8 -*-

from imio.smartweb.common.behaviors.publish import publish
from imio.smartweb.common.behaviors.publish import publish_transition
from imio.smartweb.common.behaviors.publish import type_can_publish
from imio.smartweb.common.config import DESCRIPTION_MAX_LENGTH
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from z3c.form import button
from z3c.form.interfaces import HIDDEN_MODE


class CustomAddForm(DefaultAddForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False
    # buttonAndHandler writes into the class body locals: without these copies
    # the inherited Save/Cancel buttons would be shadowed.
    buttons = DefaultAddForm.buttons.copy()
    handlers = DefaultAddForm.handlers.copy()
    added = None

    def add(self, obj):
        super(CustomAddForm, self).add(obj)
        # createAndAdd returns the object as it was before insertion; keep the
        # one actually stored in the container, needed to apply the workflow.
        self.added = self.container.get(obj.getId())

    @button.buttonAndHandler(
        _("Save and publish"),
        name="save_and_publish",
        condition=lambda form: type_can_publish(form.portal_type, form.container),
    )
    def handleAddAndPublish(self, action):
        # buttonAndHandler turned handleAdd into a Handler object, not a method
        self.handleAdd.func(self, action)
        if self.added is None:
            return
        publish(self.added, publish_transition(self.added), self.request)

    # buttonAndHandler appended the button after Cancel; put it back next to Save
    buttons = buttons.select("save", "save_and_publish", "cancel")

    def updateFields(self):
        super(CustomAddForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE
        # Description field has a maximum number of chars
        if "IBasic.description" in self.fields:
            self.fields["IBasic.description"].field.max_length = DESCRIPTION_MAX_LENGTH
        elif "IDublinCore.description" in self.fields:
            self.fields["IDublinCore.description"].field.max_length = (
                DESCRIPTION_MAX_LENGTH
            )

    def updateWidgets(self):
        super(CustomAddForm, self).updateWidgets()
        if "ILeadImageBehavior.image" in self.widgets:
            desc = _(
                "Please note that it is important to upload an image without "
                "text for design and accessibility reasons. "
                "The image will not display in its entirety and the text may be cut off."
            )
            self.widgets["ILeadImageBehavior.image"].description = desc
        # Change Description field help text
        if "IBasic.description" in self.widgets:
            self.widgets["IBasic.description"].description = _(
                "Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={"max": DESCRIPTION_MAX_LENGTH},
            )
        elif "IDublinCore.description" in self.widgets:
            self.widgets["IDublinCore.description"].description = _(
                "Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={"max": DESCRIPTION_MAX_LENGTH},
            )


class CustomAddView(DefaultAddView):
    form = CustomAddForm


class CustomEditForm(DefaultEditForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False
    # See CustomAddForm
    buttons = DefaultEditForm.buttons.copy()
    handlers = DefaultEditForm.handlers.copy()

    @button.buttonAndHandler(
        _("Save and publish"),
        name="save_and_publish",
        condition=lambda form: publish_transition(form.context) is not None,
    )
    def handleSaveAndPublish(self, action):
        # buttonAndHandler turned handleApply into a Handler object, not a method
        self.handleApply.func(self, action)
        if self.status == self.formErrorsMessage:
            return
        publish(self.context, publish_transition(self.context), self.request)

    # See CustomAddForm
    buttons = buttons.select("save", "save_and_publish", "cancel")

    def updateFields(self):
        super(CustomEditForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE
        # Description field has a maximum number of chars
        if "IBasic.description" in self.fields:
            self.fields["IBasic.description"].field.max_length = DESCRIPTION_MAX_LENGTH
        elif "IDublinCore.description" in self.fields:
            self.fields["IDublinCore.description"].field.max_length = (
                DESCRIPTION_MAX_LENGTH
            )

    def updateWidgets(self):
        super(CustomEditForm, self).updateWidgets()
        if "ILeadImageBehavior.image" in self.widgets:
            desc = _(
                "Please note that it is important to upload an image without "
                "text for design and accessibility reasons. "
                "The image will not display in its entirety and the text may be cut off."
            )
            self.widgets["ILeadImageBehavior.image"].description = desc
        # Change Description field help text
        if "IBasic.description" in self.widgets:
            self.widgets["IBasic.description"].description = _(
                "Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={"max": DESCRIPTION_MAX_LENGTH},
            )
        elif "IDublinCore.description" in self.widgets:
            self.widgets["IDublinCore.description"].description = _(
                "Use **text** to set text in bold. Limited to ${max} characters.",
                mapping={"max": DESCRIPTION_MAX_LENGTH},
            )


CustomEditView = layout.wrap_form(CustomEditForm)
