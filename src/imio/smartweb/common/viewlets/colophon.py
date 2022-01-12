# -*- coding: utf-8 -*-

from datetime import date
from plone import api
from plone.app.layout.viewlets import common


class ColophonViewlet(common.ViewletBase):
    def update(self):
        super(ColophonViewlet, self).update()
        self.year = date.today().year
        self.has_gdpr = api.portal.get_registry_record(
            "imio.gdpr.interfaces.IGDPRSettings.is_text_ready", default=False
        )
