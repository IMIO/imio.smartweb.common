# -*- coding: utf-8 -*-

from collective.privacy.browser.consent import ConsentForm
from collective.privacy.interfaces import IConsentFormView
from imio.smartweb.common.browser.privacy.utils import get_all_consent_reasons
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from z3c.form import button
from zope.i18n import translate

import os


class ConsentFormWithPolicy(ConsentForm):

    label = _("Cookies choice")
    id = "cookies-form"

    def update(self):
        super(ConsentFormWithPolicy, self).update()
        root = api.portal.get_navigation_root(self.context)
        current_lang = api.portal.get_current_language()[:2]
        policy_url = "{}/@@cookies-view".format(root.absolute_url())
        description = _(
            "Choose to opt in or out of cookies use.<br/>"
            'Our <a href="${policy_url}">cookies policy</a> can help you choose.',
            mapping={"policy_url": policy_url},
        )
        self.description = translate(description, target_language=current_lang)

    @button.buttonAndHandler(_("Save my choices"))
    def handleApply(self, action):
        super(ConsentFormWithPolicy, self).handleApply(self, action)

    @button.buttonAndHandler(_("Accept all"))
    def handleAcceptAll(self, action):
        privacy_tool = api.portal.get_tool("portal_privacy")
        for reason in get_all_consent_reasons(privacy_tool):
            privacy_tool.consentToProcessing(reason.__name__)

    @button.buttonAndHandler(_("Refuse all"))
    def handleRefuseAll(self, action):
        privacy_tool = api.portal.get_tool("portal_privacy")
        for reason in get_all_consent_reasons(privacy_tool):
            privacy_tool.objectToProcessing(reason.__name__)


form_factory = ZopeTwoFormTemplateFactory(
    os.path.join(os.path.dirname(__file__), "form.pt"),
    form=IConsentFormView,
    request=IPloneFormLayer,
)
