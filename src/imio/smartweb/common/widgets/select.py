# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import ITranslatedAjaxSelectWidget
from plone import api
from plone.app.z3cform.widgets.select import AjaxSelectWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only
from zope.i18n import translate


@implementer_only(ITranslatedAjaxSelectWidget)
class TranslatedAjaxSelectWidget(AjaxSelectWidget):
    """Translated Ajax select widget for z3c.form."""

    def _ajaxselect_options(self):
        options = super(TranslatedAjaxSelectWidget, self)._ajaxselect_options()
        current_lang = api.portal.get_current_language()[:2]
        translated_initial_values = {}
        for token, value in list(options.get("initialValues", {}).items()):
            translated_initial_values[token] = translate(
                value, domain="imio.smartweb", target_language=current_lang
            )
        if translated_initial_values:
            options["initialValues"] = translated_initial_values
        return options


@implementer(IFieldWidget)
def TranslatedAjaxSelectFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, TranslatedAjaxSelectWidget(request))
