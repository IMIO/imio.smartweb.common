# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18n import translate
from zope.i18n.locales import locales
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json


class TopicsVocabularyFactory:
    def __call__(self, context=None):
        topics = [
            ("entertainment", _("Entertainment")),
            ("agriculture", _("Agriculture")),
            ("citizenship", _("Citizenship")),
            ("culture", _("Culture")),
            ("economics", _("Economics")),
            ("education", _("Education")),
            ("environment", _("Environment")),
            ("habitat_town_planning", _("Habitat and town planning")),
            ("mobility", _("Mobility")),
            ("citizen_participation", _("Citizen participation")),
            ("politics", _("Politics")),
            ("health", _("Health")),
            ("safety_prevention", _("Safety and prevention")),
            ("social", _("Social")),
            ("sports", _("Sports")),
            ("territory_public_space", _("Territory and public space")),
            ("tourism", _("Tourism")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in topics]
        return SimpleVocabulary(terms)


TopicsVocabulary = TopicsVocabularyFactory()


class TopicsDeVocabularyFactory:
    def __call__(self, context=None):
        vocabulary = TopicsVocabularyFactory()(context)
        translated_terms = [
            SimpleTerm(
                value=term.value,
                token=term.token,
                title=translate(term.title, target_language="de"),
            )
            for term in vocabulary
        ]
        return SimpleVocabulary(translated_terms)


TopicsDeVocabulary = TopicsDeVocabularyFactory()


class IAmVocabularyFactory:
    def __call__(self, context=None):
        iam = [
            ("merchant", _("Merchant")),
            ("job_seeker", _("Job seeker")),
            ("disabled_person", _("Disabled person")),
            ("young", _("Young")),
            ("journalist", _("Journalist")),
            ("newcomer", _("Newcomer")),
            ("event_planner", _("Event planner")),
            ("parent", _("Parent")),
            ("elder", _("Elder")),
            ("tourist", _("Tourist")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in iam]
        return SimpleVocabulary(terms)


IAmVocabulary = IAmVocabularyFactory()


class IAmDeVocabularyFactory:
    def __call__(self, context=None):
        vocabulary = IAmVocabularyFactory()(context)
        translated_terms = [
            SimpleTerm(
                value=term.value,
                token=term.token,
                title=translate(term.title, target_language="de"),
            )
            for term in vocabulary
        ]
        return SimpleVocabulary(translated_terms)


IAmDeVocabulary = IAmDeVocabularyFactory()


class CountriesVocabularyFactory:
    def __call__(self, context=None, lang=None):
        normalizer = getUtility(IIDNormalizer)
        if lang is None:
            lang = api.portal.get_current_language()
        locale = locales.getLocale(lang)
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
                city["zip"], city["zip"], "{0} {1}".format(city["zip"], city["city"])
            )
            for city in cities
        ]
        return SimpleVocabulary(terms)


CitiesVocabulary = CitiesVocabularyFactory()


class ScalesVocabularyFactory:
    def __call__(self, context=None):
        topics = [
            ("affiche", _("Affiche")),
            ("vignette", _("Vignette")),
            ("liste", _("Liste")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in topics]
        return SimpleVocabulary(terms)


ScalesVocabulary = ScalesVocabularyFactory()
