# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class TopicsVocabularyFactory:
    def __call__(self, context=None):
        topics = [
            (u"martial_arts", _(u"Martial arts")),
            (u"concert", _(u"Concert")),
            (u"education", _(u"Education")),
            (u"climbing", _(u"Climbing")),
            (u"museum", _(u"Museum")),
            (u"sport", _(u"Sport")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in topics]
        return SimpleVocabulary(terms)


TopicsVocabulary = TopicsVocabularyFactory()


class IAmVocabularyFactory:
    def __call__(self, context=None):
        topics = [
            (u"student", _(u"Student")),
            (u"elder", _(u"Elder")),
            (u"parent", _(u"Parent")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in topics]
        return SimpleVocabulary(terms)


IAmVocabulary = IAmVocabularyFactory()
