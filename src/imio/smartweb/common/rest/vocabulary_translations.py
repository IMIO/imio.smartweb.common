# -*- coding: utf-8 -*-

from plone.restapi.services.vocabularies.get import VocabulariesGet
from zope.component import ComponentLookupError
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory

LANGUAGES = ["fr", "nl", "de", "en"]


class VocabularyTranslationsGet(VocabulariesGet):
    """Return the terms of a vocabulary with their title in each language.

    GET /@vocabulary-translations/<vocabulary_name>
    """

    def reply(self):
        if len(self.params) != 1:
            return self._error(
                400, "Bad Request", "You must give exactly one vocabulary name"
            )
        vocabulary_name = self.params[0]

        if not self._has_permission_to_access_vocabulary(vocabulary_name):
            # Same answers as @vocabularies
            if self.context.portal_membership.isAnonymousUser():
                return self._error(401, "Not authenticated", "Not authenticated")
            return self._error(403, "Not authorized", "Not authorized")

        try:
            factory = getUtility(IVocabularyFactory, name=vocabulary_name)
        except ComponentLookupError:
            return self._error(
                404, "Not Found", f"The vocabulary '{vocabulary_name}' does not exist"
            )

        items = [
            {
                "token": term.token,
                **{
                    lang: translate(term.title or term.token, target_language=lang)
                    for lang in LANGUAGES
                },
            }
            for term in factory(self.context)
        ]
        return {
            "@id": f"{self.context.absolute_url()}/@vocabulary-translations/{vocabulary_name}",
            "items": items,
            "items_total": len(items),
        }
