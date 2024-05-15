# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class SkipToContentViewlet(common.ViewletBase):
    index = ViewPageTemplateFile("skip_to_content.pt")

    def update(self):
        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )
        self.current_page_url = context_state.current_page_url
