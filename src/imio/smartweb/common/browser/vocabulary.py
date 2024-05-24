# -*- coding: utf-8 -*-

from plone import api
from plone.app.content.browser.vocabulary import VocabularyView
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from zope.i18n import translate


class TranslatedVocabularyView(VocabularyView):

    def __call__(self):
        """
        Translate texts in JSON response
        `@getVocabulary` does not do it and returns English values
        """
        result = super(TranslatedVocabularyView, self).__call__()
        json = json_loads(result)
        if int(json.get("total", 0)) == 0:
            return result
        lang = api.portal.get_current_language()[:2]
        for item in json["results"]:
            if "text" in item:
                item["text"] = translate(
                    item["text"], domain="imio.smartweb", target_language=lang
                )
        return json_dumps(json)
