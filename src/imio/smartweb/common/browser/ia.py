from zope.publisher.browser import BrowserView

import os


class BaseIAView(BrowserView):
    """
    Base view providing common headers and configuration for IA-related features.
    This class is shared across multiple projects, including imio.smartweb.core.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        project_id = os.environ.get("PROJECT_ID", "smartweb")
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "x-imio-application": "smartweb",
            "x-imio-municipality": project_id,
        }
