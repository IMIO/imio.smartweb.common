# -*- coding: utf-8 -*-

from plone import api
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import geopy


def get_term_from_vocabulary(vocabulary, value):
    factory = getUtility(IVocabularyFactory, vocabulary)
    vocabulary = factory()
    term = vocabulary.getTerm(value)
    return term


def translate_vocabulary_term(vocabulary, term):
    if term is None:
        return ""
    factory = getUtility(IVocabularyFactory, vocabulary)
    vocabulary = factory(api.portal.get())
    term = vocabulary.getTerm(term)
    return term and term.title or ""


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
        obj.geolocation.latitude = location.latitude
        obj.geolocation.longitude = location.longitude
    obj.reindexObject(idxs=["longitude", "latitude"])
