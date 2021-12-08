# -*- coding: utf-8 -*-

from plone import api
from plone.formwidget.geolocation.geolocation import Geolocation
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm

import geopy


def get_vocabulary(voc_name):
    factory = getUtility(IVocabularyFactory, voc_name)
    vocabulary = factory(api.portal.get())
    return vocabulary


def get_term_from_vocabulary(vocabulary, value):
    portal = api.portal.get()
    factory = getUtility(IVocabularyFactory, vocabulary)
    vocabulary = factory(portal)
    try:
        term = vocabulary.getTerm(value)
    except LookupError:
        return SimpleTerm(value=value, title=value)
    return term


def translate_vocabulary_term(vocabulary, term):
    if term is None:
        return ""
    portal = api.portal.get()
    factory = getUtility(IVocabularyFactory, vocabulary)
    vocabulary = factory(portal)
    term = vocabulary.getTerm(term)
    if term is None:
        return ""
    current_lang = api.portal.get_current_language()[:2]
    return translate(term.title, target_language=current_lang)


def geocode_object(obj):
    street_parts = [
        obj.number and str(obj.number) or "",
        obj.street,
        obj.complement,
    ]
    street = " ".join(filter(None, street_parts))
    entity_parts = [
        obj.zipcode and str(obj.zipcode) or "",
        obj.city,
    ]
    entity = " ".join(filter(None, entity_parts))
    country = translate_vocabulary_term(
        "imio.smartweb.vocabulary.Countries", obj.country
    )
    address = " ".join(filter(None, [street, entity, country]))
    if not address:
        return
    geolocator = geopy.geocoders.Nominatim(user_agent="contact@imio.be", timeout=3)
    location = geolocator.geocode(address)
    if location:
        obj.geolocation = Geolocation(
            latitude=location.latitude, longitude=location.longitude
        )
        obj.reindexObject(idxs=["longitude", "latitude"])
        return True
    return False
