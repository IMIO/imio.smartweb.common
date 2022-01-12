# -*- coding: utf-8 -*-

from collective.privacy.browser.consent import ConsentForm
from collective.privacy.interfaces import IConsentFormView
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from z3c.form import button
from zope.i18n import translate

import os


class ConsentFormWithPolicy(ConsentForm):
    def update(self):
        super(ConsentFormWithPolicy, self).update()
        root = api.portal.get_navigation_root(self.context)
        current_lang = api.portal.get_current_language()[:2]
        policy_url = u"{}/@@cookies-view".format(root.absolute_url())
        description = _(
            u"Choose to opt in or out of various pieces of functionality.<br/>"
            u'If you want, you can <a href="${policy_url}">read our cookie policy</a>.',
            mapping={u"policy_url": policy_url},
        )
        self.description = translate(description, target_language=current_lang)

    @button.buttonAndHandler(_(u"Save"))
    def handleApply(self, action):
        super(ConsentFormWithPolicy, self).handleApply(self, action)


form_factory = ZopeTwoFormTemplateFactory(
    os.path.join(os.path.dirname(__file__), "form.pt"),
    form=IConsentFormView,
    request=IPloneFormLayer,
)
