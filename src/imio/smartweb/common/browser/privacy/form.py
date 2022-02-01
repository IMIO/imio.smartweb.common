# -*- coding: utf-8 -*-

from collective.privacy.browser.consent import ConsentForm
from imio.smartweb.common.browser.privacy.utils import get_all_consent_reasons
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from z3c.form import button
from zope.i18n import translate


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
