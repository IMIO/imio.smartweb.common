# -*- coding: utf-8 -*-

from plone.restapi.services.vocabularies.get import (
    VocabulariesGet as BaseVocabulariesGet,
)


class VocabulariesGet(BaseVocabulariesGet):
    def reply(self):
        return super(VocabulariesGet, self).reply()
