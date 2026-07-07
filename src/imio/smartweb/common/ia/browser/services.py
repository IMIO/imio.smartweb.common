from imio.helpers.ws import get_auth_token
from imio.omnia.core.interfaces import IOmniaCoreAPIService
from imio.omnia.core.services import OmniaCoreAPIService
from imio.smartweb.common.interfaces import IImioSmartwebCommonLayer
from imio.smartweb.common.utils import is_log_active
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import logging

logger = logging.getLogger(__name__)


@adapter(Interface, IImioSmartwebCommonLayer)
@implementer(IOmniaCoreAPIService)
class TokenAuthCoreAPIService(OmniaCoreAPIService):
    """Adapter to keep OmniaCoreAPIService and improve authentication
    with last minute bearer token"""

    def _headers(self):
        headers = super()._headers()
        try:
            token = get_auth_token()
            if isinstance(token, str) and token:
                headers["Authorization"] = f"Bearer {token}"
            if is_log_active():
                logger.info("Authorization header set")
        except Exception:
            logger.warning(
                "Could not retrieve auth token; proceeding without "
                "Authorization header",
                exc_info=True,
            )
        return headers
