# -*- coding: utf-8 -*-

from plone import api

import logging
import os
import requests

logger = logging.getLogger("imio.smartweb.common")


def ban_physicalpath(request, physical_path):
    portal = api.portal.get()
    caching_servers = os.environ.get("CACHING_SERVERS", "").split(" ")
    forwarded_host = request.get("X-Forwarded-Host", "")
    headers = {"Host": forwarded_host}
    len_portal_path = len(portal.getPhysicalPath())
    path = "/".join(physical_path[len_portal_path:])
    for caching_server in caching_servers:
        if not caching_server:
            continue
        if path:
            ban_url = f"http://{caching_server}/{path}"
        else:
            ban_url = f"http://{caching_server}"
        logger.info(
            f"## BAN ## X-Forwarded-Host : {forwarded_host} ## ban_url : {ban_url}"
        )
        requests.request("BAN", ban_url, headers=headers)
