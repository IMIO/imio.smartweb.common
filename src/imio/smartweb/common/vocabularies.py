# -*- coding: utf-8 -*-
from imio.smartweb.common.config import DIRECTORY_URL
from imio.smartweb.common.utils import get_entities_vocabulary
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from time import time
from zope.component import getUtility
from zope.i18n import translate
from zope.i18n.locales import locales
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json

# The remote directory is reachable over HTTP only, so its entities vocabulary
# is cached. Unlike the other vocabularies here it is not frozen — a client
# adding an entity must see it appear — hence a TTL rather than a permanent
# memoization. 300s absorbs bursts of form renderings without making a fresh
# entity feel lost.
DIRECTORY_ENTITIES_CACHE_TTL = 300


def _translate_vocabulary(vocabulary, target_language):
    """Eagerly translate a vocabulary's titles into a fixed language.

    Only for vocabularies whose language is fixed at registration time. The
    result is a plain string per title, so it must never be used for the
    current request's language.
    """
    return SimpleVocabulary(
        [
            SimpleTerm(
                value=term.value,
                token=term.token,
                title=translate(term.title, target_language=target_language),
            )
            for term in vocabulary
        ]
    )


# Every factory below is registered in vocabularies.zcml with `component=`, not
# `factory=`, so the utility is the module-level singleton instantiated at the
# end of each class. That is what makes the `_vocabulary` / `_cache` attributes
# survive across calls: switching those registrations to `factory=` would
# silently disable every cache in this module.


class TopicsVocabularyFactory:
    def __call__(self, context=None):
        if not hasattr(self, "_vocabulary"):
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
            self._vocabulary = SimpleVocabulary(terms)
        return self._vocabulary


TopicsVocabulary = TopicsVocabularyFactory()


class TopicsDeVocabularyFactory:
    def __call__(self, context=None):
        if not hasattr(self, "_vocabulary"):
            # Safe to memoize the translated titles: the target language is
            # hardcoded, so the result depends on neither the request nor the
            # portal's current language.
            self._vocabulary = _translate_vocabulary(TopicsVocabulary(context), "de")
        return self._vocabulary


TopicsDeVocabulary = TopicsDeVocabularyFactory()


class IAmVocabularyFactory:
    def __call__(self, context=None):
        if not hasattr(self, "_vocabulary"):
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
            self._vocabulary = SimpleVocabulary(terms)
        return self._vocabulary


IAmVocabulary = IAmVocabularyFactory()


class IAmDeVocabularyFactory:
    def __call__(self, context=None):
        if not hasattr(self, "_vocabulary"):
            # Safe to memoize the translated titles: the target language is
            # hardcoded, so the result depends on neither the request nor the
            # portal's current language.
            self._vocabulary = _translate_vocabulary(IAmVocabulary(context), "de")
        return self._vocabulary


IAmDeVocabulary = IAmDeVocabularyFactory()


class CountriesVocabularyFactory:
    def __call__(self, context=None, lang=None):
        normalizer = getUtility(IIDNormalizer)
        if lang is None:
            lang = api.portal.get_current_language()
        attr_name = f"_vocabulary_{lang}"
        if not hasattr(self, attr_name):
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
            setattr(self, attr_name, SimpleVocabulary(terms))
        return getattr(self, attr_name)


CountriesVocabulary = CountriesVocabularyFactory()


class CitiesVocabularyFactory:
    """Belgian cities, memoized for the whole lifetime of the process.

    The `imio.smartweb.cities` registry record holds the exhaustive list of
    Belgian zip codes and is not expected to ever gain entries, so this
    memoization is deliberate and must not be invalidated. Note that the
    singleton is shared by every Plone site running in the process, which
    assumes they all carry that same exhaustive list.
    """

    def __call__(self, context=None):
        if not hasattr(self, "_vocabulary"):
            registry = getUtility(IRegistry)
            json_str = registry.get("imio.smartweb.cities")
            cities = json.loads(json_str)
            terms = [
                SimpleVocabulary.createTerm(
                    city["zip"],
                    city["zip"],
                    "{0} {1}".format(city["zip"], city["city"]),
                )
                for city in cities
            ]
            self._vocabulary = SimpleVocabulary(terms)
        return self._vocabulary


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


class RemoteDirectoryEntitiesVocabularyFactory:
    # A dict rather than a single slot: with the language in the key, a single
    # slot would make alternating fr/de traffic evict itself down to a 0% hit
    # rate. Bounded in practice by (configured urls x active languages), so it
    # needs no eviction policy.
    _cache = {}

    def __call__(self, context=None):
        directory_url = (
            api.portal.get_registry_record(
                "imio.smartweb.common.directory_url", default=""
            )
            or DIRECTORY_URL
        )
        # get_json negotiates the current language into the remote @search
        # (utils.py:41-43), so the language is part of the cache identity, not
        # just the url. The url is in the key too, so changing the registry
        # record invalidates at once instead of waiting for the deadline.
        key = (directory_url, api.portal.get_current_language())
        cached = self._cache.get(key)
        if cached is not None and cached[0] > time():
            return cached[1]
        vocabulary = get_entities_vocabulary("imio.directory.Entity", directory_url)
        if len(vocabulary) > 0:
            # Only cache a successful fetch: get_entities_vocabulary returns an
            # empty vocabulary when the http call fails, and freezing that for
            # the whole TTL would empty the entity list in every form.
            self._cache[key] = (time() + DIRECTORY_ENTITIES_CACHE_TTL, vocabulary)
        return vocabulary


RemoteDirectoryEntitiesVocabulary = RemoteDirectoryEntitiesVocabularyFactory()


class ContactBlocksVocabularyFactory:
    def __call__(self, context=None):
        values = [
            ("logo", _("Logo")),
            ("leadimage", _("Lead Image")),
            ("titles", _("Title and Subtitle")),
            ("contact_informations", _("Contact informations")),
            ("address", _("Address")),
            ("itinerary", _("Itinerary")),
            ("schedule", _("Schedule")),
            ("map", _("Map")),
            ("description", _("Description")),
            ("gallery", _("Gallery")),
        ]
        terms = [
            SimpleVocabulary.createTerm(value[0], value[0], value[1])
            for value in values
        ]
        return SimpleVocabulary(terms)


ContactBlocksVocabulary = ContactBlocksVocabularyFactory()
