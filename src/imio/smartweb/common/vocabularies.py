# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18n.locales import locales
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json


class TopicsVocabularyFactory:
    def __call__(self, context=None):
        topics = [
            (u"entertainment", _(u"Entertainment")),
            (u"agriculture", _(u"Agriculture")),
            (u"citizenship", _(u"Citizenship")),
            (u"culture", _(u"Culture")),
            (u"economics", _(u"Economics")),
            (u"education", _(u"Education")),
            (u"environment", _(u"Environment")),
            (u"habitat_town_planning", _(u"Habitat and town planning")),
            (u"mobility", _(u"Mobility")),
            (u"citizen_participation", _(u"Citizen participation")),
            (u"politics", _(u"Politics")),
            (u"health", _(u"Health")),
            (u"safety_prevention", _(u"Safety and prevention")),
            (u"social", _(u"Social")),
            (u"sports", _(u"Sports")),
            (u"territory_public_space", _(u"Territory and public space")),
            (u"tourism", _(u"Tourism")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in topics]
        return SimpleVocabulary(terms)


TopicsVocabulary = TopicsVocabularyFactory()


class IAmVocabularyFactory:
    def __call__(self, context=None):
        iam = [
            (u"merchant", _(u"Merchant")),
            (u"job_seeker", _(u"Job seeker")),
            (u"disabled_person", _(u"Disabled person")),
            (u"young", _(u"Young")),
            (u"journalist", _(u"Journalist")),
            (u"newcomer", _(u"Newcomer")),
            (u"event_planner", _(u"Event planner")),
            (u"parent", _(u"Parent")),
            (u"elder", _(u"Elder")),
            (u"tourist", _(u"Tourist")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in iam]
        return SimpleVocabulary(terms)


IAmVocabulary = IAmVocabularyFactory()


class CountriesVocabularyFactory:
    def __call__(self, context=None):
        normalizer = getUtility(IIDNormalizer)
        current_language = api.portal.get_current_language()
        locale = locales.getLocale(current_language)
        localized_country_names = {
            capitalized_code.lower(): translation
            for capitalized_code, translation in locale.displayNames.territories.items()
        }
        terms = [
            SimpleTerm(value=k, token=k, title=v)
            for k, v in sorted(
                localized_country_names.items(),
                key=lambda kv: normalizer.normalize(kv[1]),
            )
            if k != "fallback"
        ]
        return SimpleVocabulary(terms)


CountriesVocabulary = CountriesVocabularyFactory()


class CitiesVocabularyFactory:
    def __call__(self, context=None):
        registry = getUtility(IRegistry)
        json_str = registry.get("imio.smartweb.cities")
        cities = json.loads(json_str)
        terms = [
            SimpleVocabulary.createTerm(
                city["zip"], city["zip"], u"{0} {1}".format(city["zip"], city["city"])
            )
            for city in cities
        ]
        return SimpleVocabulary(terms)


CitiesVocabulary = CitiesVocabularyFactory()
