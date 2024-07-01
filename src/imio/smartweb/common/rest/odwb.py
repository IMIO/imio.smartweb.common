# -*- coding: utf-8 -*-

from imio.smartweb.common.utils import activate_sending_data_to_odwb_for_staging
from imio.smartweb.common.utils import is_staging_or_local
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.interface import Interface

import logging
import requests

logger = logging.getLogger("imio.smartweb.common")


class IOdwbService(Interface):

    def available():
        """ """

    def reply():
        """ """

    def remove():
        """ """


@implementer(IOdwbService)
class OdwbService(Service):

    def available(self):
        staging_or_local = is_staging_or_local()
        if staging_or_local:
            if activate_sending_data_to_odwb_for_staging() is True:
                return True
            logger.info(
                "Don't send odwb data when we are in staging or local environment"
            )
        return not staging_or_local


class OdwbBaseEndpointGet(OdwbService):

    def __init__(self, context, request, odwb_imio_service, odbw_pushkey):
        self.odwb_api_push_url = "https://www.odwb.be/api/push/1.0"
        self.odwb_imio_service = odwb_imio_service
        self.odwb_pushkey = api.portal.get_registry_record(odbw_pushkey)

        self.context = context
        self.request = request
        self.__datas__ = []

    def odwb_query(self, url, payload, headers=None):
        if headers is None:
            headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, data=payload)
            return response.text
        except requests.exceptions.ConnectionError as e:
            logger.error("ODWB : Connection error: %s", e)
            return "ODWB : Connection error occurred"
        except requests.exceptions.Timeout as e:
            logger.error("ODWB : Request timed out: %s", e)
            return "ODWB : Request timed out"
        except requests.exceptions.HTTPError as e:
            logger.error("ODWB : HTTP error occurred: %s", e)
            return "ODWB : HTTP error occurred"
        except Exception as e:
            logger.error("ODWB : An unexpected error occurred: %s", e)
            return "ODWB : Unexpected error occurred"
