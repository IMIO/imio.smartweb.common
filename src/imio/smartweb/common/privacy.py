# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.transformchain.interfaces import ITransform
from zope.component import adapter
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


def replace_iframe(soup, message):
    """
    Change <iframe> attributes to make it work only if cookies have been accepted
    The iframe attributes are put back through JS (to avoid server caching)
    """
    privacy_tag = soup.new_tag("div")
    privacy_tag.append(BeautifulSoup(message, "html.parser"))
    privacy_tag["class"] = "gdpr-iframe-message"
    tags = soup.findAll("iframe")
    for tag in tags:
        tag["gdpr-src"] = tag["src"]
        tag["src"] = ""
        if tag.get("width"):
            tag["gdpr-width"] = tag["width"]
        if tag.get("height"):
            tag["gdpr-height"] = tag["height"]
        tag["width"] = tag["height"] = "0"
        tag["class"] = "gdpr-iframe"
        tag.insert_after(privacy_tag)


@implementer(ITransform)
@adapter(Interface, Interface)
class EmbedTransform(object):

    order = 1000000

    def __init__(self, published, request):
        self.published = published
        self.request = request
        self.message = None

    def applyTransform(self):
        site = getSite()
        if not site:
            return False
        if self.published is None:
            return False
        responseType = self.request.response.getHeader("content-type") or ""
        if not responseType.startswith("text/html") and not responseType.startswith(
            "text/xhtml"
        ):
            return False
        return True

    def prepareMessage(self):
        if self.message:
            return
        current_lang = api.portal.get_current_language()[:2]
        root = api.portal.get_navigation_root(self.published)
        if not IDexterityContent.providedBy(root):
            root = api.portal.get()
        consent_url = u"{}/@@consent".format(root.absolute_url())
        message = _(
            u"This feature requires cookies acceptation.<br/>"
            u'Please <a class="pat-plone-modal" href="${consent_url}">review your cookies preferences</a>.',
            mapping={u"consent_url": consent_url},
        )
        self.message = translate(message, target_language=current_lang)

    def transformBytes(self, result, encoding):
        if not self.applyTransform():
            return result
        soup = BeautifulSoup(result, "lxml")
        self.prepareMessage()
        replace_iframe(soup, self.message)
        return str(soup)

    def transformUnicode(self, result, encoding):
        if not self.applyTransform():
            return result
        soup = BeautifulSoup(result, "lxml")
        self.prepareMessage()
        replace_iframe(soup, self.message)
        return str(soup)

    def transformIterable(self, result, encoding):
        if not self.applyTransform():
            return result
        self.prepareMessage()
        transformed = []
        for r in result:
            soup = BeautifulSoup(r, "lxml")
            replace_iframe(soup, self.message)
            transformed.append(str(soup))
        return transformed
