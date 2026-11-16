# -*- coding: utf-8 -*-

from plone import api
from plone.app.caching.interfaces import IETagValue
from plone.registry.interfaces import IRegistry
from urllib.parse import urlparse
from zope.component import adapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface

import logging
import os
import requests
import time
import transaction

logger = logging.getLogger("imio.smartweb.common")

BAN_TIMEOUT = 5

# Registry attribute holding the time of the site's last BAN, used as ETag
_LAST_BAN = "__IMIO_SMARTWEB_LAST_BAN"


def ban_physicalpath(request, physical_path):
    portal = api.portal.get()
    caching_servers = os.environ.get("CACHING_SERVERS", "").split(" ")
    website_hostname = (
        os.environ.get("WEBSITE_HOSTNAME", "") or urlparse(portal.absolute_url()).netloc
    )
    headers = {"Host": website_hostname}
    len_portal_path = len(portal.getPhysicalPath())
    path = "/".join(physical_path[len_portal_path:])
    # The banned pages show content outside their own validators (messages,
    # footer, hero banner): change their ETag so browsers don't get a 304
    registry = queryUtility(IRegistry)
    if registry is not None:
        setattr(registry, _LAST_BAN, time.time())
    # Ban once the change is committed: a request served before the commit
    # would put the old content back in the cache
    transaction.get().addAfterCommitHook(
        _send_bans, args=(caching_servers, website_hostname, headers, path)
    )


def _send_bans(committed, caching_servers, website_hostname, headers, path):
    if not committed:
        return
    for caching_server in caching_servers:
        if not caching_server:
            continue
        if path:
            ban_url = f"http://{caching_server}/{path}"
        else:
            ban_url = f"http://{caching_server}"
        logger.info(
            f"## BAN ## website_hostname : {website_hostname} ## ban_url : {ban_url}"
        )
        try:
            requests.request("BAN", ban_url, headers=headers, timeout=BAN_TIMEOUT)
        except requests.exceptions.RequestException:
            logger.exception(f"## BAN ## failed for ban_url : {ban_url}")


@implementer(IETagValue)
@adapter(Interface, Interface)
class LastBan:
    """The ``lastBan`` etag component, returning the time of the site's last
    BAN
    """

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        registry = queryUtility(IRegistry)
        last_ban = getattr(registry, _LAST_BAN, None)
        if last_ban is None:
            return
        return str(last_ban)
