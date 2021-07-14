# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class TopicsVocabularyFactory:
    def __call__(self, context=None):
        topics = [
            (u"culture", _(u"Culture")),
            (u"agriculture", _(u"Agriculture")),
            (u"education", _(u"Education")),
            (u"environment", _(u"Environment")),
            (u"health", _(u"Health")),
            (u"sports", _(u"Sports")),
            (u"territory_town_planning", _(u"Territory & town planning")),
            (u"economic_life", _(u"Economic life")),
            (u"political_life", _(u"Political life")),
            (u"habitat", _(u"Habitat")),
            (u"mobility", _(u"Mobility")),
            (u"tourism", _(u"Tourism")),
            (u"social", _(u"Social")),
            (u"citizen_participation", _(u"Citizen participation")),
            (u"entertainment", _(u"Entertainment")),
            (u"safety_prevention", _(u"Safety & prevention")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in topics]
        return SimpleVocabulary(terms)


TopicsVocabulary = TopicsVocabularyFactory()


class IAmVocabularyFactory:
    def __call__(self, context=None):
        iam = [
            (u"elder", _(u"Elder")),
            (u"young", _(u"Young")),
            (u"merchant", _(u"Merchant")),
            (u"journalist", _(u"Journalist")),
            (u"newcomer", _(u"Newcomer")),
            (u"tourist", _(u"Tourist")),
            (u"parent", _(u"Parent")),
            (u"disabled_person", _(u"Disabled person")),
            (u"job_seeker", _(u"Job seeker")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in iam]
        return SimpleVocabulary(terms)


IAmVocabulary = IAmVocabularyFactory()
