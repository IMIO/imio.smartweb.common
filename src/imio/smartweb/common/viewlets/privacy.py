# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common
from urllib.parse import urljoin


class PrivacyViewlet(common.ViewletBase):
    @property
    def rebuild_url(self):
        form_data = self.request.form
        if form_data is not None:
            url = urljoin(
                self.request.ACTUAL_URL,
                "?" + "&".join([f"{key}={value}" for key, value in form_data.items()]),
            )
        return url
