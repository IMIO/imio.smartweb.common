# -*- coding: utf-8 -*-

from imio.smartweb.common.sso import REGISTRY_PREFIX
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import field
from z3c.form.browser.password import PasswordFieldWidget
from zope import schema
from zope.interface import Interface


class ISsoSettings(Interface):
    """Authentication used by this site to call other iMio applications
    (ex: events calls smartweb sites)."""

    force_basic_auth = schema.Bool(
        title=_("Use basic auth to call other iMio applications"),
        description=_(
            "If selected, this site does not use the SSO token: it uses the user and password below. The user must exist in the called sites."
        ),
        required=False,
        default=False,
    )

    basic_auth_username = schema.TextLine(
        title=_("Basic auth username"),
        required=False,
    )

    basic_auth_password = schema.Password(
        title=_("Basic auth password"),
        required=False,
    )


class SsoControlPanelForm(RegistryEditForm):
    schema = ISsoSettings
    schema_prefix = REGISTRY_PREFIX
    label = _("Authentication between iMio applications")
    fields = field.Fields(ISsoSettings)
    fields["basic_auth_password"].widgetFactory = PasswordFieldWidget

    def applyChanges(self, data):
        # The password widget is empty when the form is shown:
        # keep the registry value if no new password is given.
        if not data.get("basic_auth_password"):
            data["basic_auth_password"] = api.portal.get_registry_record(
                f"{REGISTRY_PREFIX}.basic_auth_password"
            )
        return super().applyChanges(data)

    def updateWidgets(self):
        super().updateWidgets()
        if api.portal.get_registry_record(f"{REGISTRY_PREFIX}.basic_auth_password"):
            self.widgets["basic_auth_password"].placeholder = _(
                "Password already filled"
            )


SsoControlPanelView = layout.wrap_form(SsoControlPanelForm, ControlPanelFormWrapper)
