# -*- coding: utf-8 -*-

from imio.smartweb.common.utils import activate_sending_data_to_odwb_for_staging
from imio.smartweb.common.utils import is_log_active
from imio.smartweb.common.utils import is_staging_or_local
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.interface import Interface

import itertools
import json
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

    def hide_pushkey(self, text):
        """Return text (an url, an error...) with the ODWB pushkey masked, for logs."""
        text = str(text)
        if not self.odwb_pushkey:
            return text
        return text.replace(self.odwb_pushkey, "***")

    def odwb_send(self, items, action="push", batch_size=1000):
        """Send items (any iterable) to ODWB by batches and return a summary:
        {"service", "total", "sent", "batches": [{"size", "status_code", "response"}]}.
        action is "push" (add / update) or "delete".
        sent counts the items of the batches that ODWB accepted (HTTP 2xx)."""
        url = f"{self.odwb_api_push_url}/{self.odwb_imio_service}/temps_reel/{action}/?pushkey={self.odwb_pushkey}"
        if is_log_active():
            logger.info(f"ODWB {action} url: {self.hide_pushkey(url)}")
        batches = []
        items = iter(items)
        while batch := list(itertools.islice(items, batch_size)):
            result = self.odwb_post(url, json.dumps(batch))
            batches.append({"size": len(batch), **result})
            success = result["status_code"] in range(200, 300)
            logger.log(
                logging.INFO if success else logging.WARNING,
                "ODWB %s %s: %d item(s), status %s, response: %s",
                self.odwb_imio_service,
                action,
                len(batch),
                result["status_code"],
                result["response"],
            )
        return {
            "service": self.odwb_imio_service,
            "total": sum(batch["size"] for batch in batches),
            "sent": sum(
                batch["size"]
                for batch in batches
                if batch["status_code"] in range(200, 300)
            ),
            "batches": batches,
        }

    def odwb_query(self, url, payload, headers=None):
        return self.odwb_post(url, payload, headers)["response"]

    def odwb_post(self, url, payload, headers=None):
        """POST payload to ODWB and return {"status_code": ..., "response": ...}.
        status_code is None when ODWB could not be reached."""
        if headers is None:
            headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                url, headers=headers, data=payload, timeout=(5, 30)
            )
            return {"status_code": response.status_code, "response": response.text}
        except requests.exceptions.ConnectionError as e:
            logger.error("ODWB : Connection error: %s", self.hide_pushkey(e))
            error = "ODWB : Connection error occurred"
        except requests.exceptions.Timeout as e:
            logger.error("ODWB : Request timed out: %s", self.hide_pushkey(e))
            error = "ODWB : Request timed out"
        except requests.exceptions.HTTPError as e:
            logger.error("ODWB : HTTP error occurred: %s", self.hide_pushkey(e))
            error = "ODWB : HTTP error occurred"
        except Exception as e:
            logger.error(
                "ODWB : An unexpected error occurred: %s", self.hide_pushkey(e)
            )
            error = "ODWB : Unexpected error occurred"
        return {"status_code": None, "response": error}
