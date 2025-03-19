# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import ICropping
from operator import itemgetter
from plone.app.imagecropping.browser.editor import CroppingEditor
from plone.app.imagecropping.browser.settings import ISettings
from plone.app.imagecropping.dx import CroppingImageScalingFactory
from plone.app.imagecropping.storage import Storage
from plone.namedfile.interfaces import IAvailableSizes
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import six


class SmartwebCroppingEditor(CroppingEditor):
    def _scale_info(self, fieldname, scale_id, target_size, true_size):
        scale = super(SmartwebCroppingEditor, self)._scale_info(
            fieldname, scale_id, target_size, true_size
        )
        title = scale["title"]
        if "portrait" in title or "paysage" in title or "carre" in title:
            # remove orientation part from scale title
            title = title.split("_")[0]
        scale["title"] = title.title()
        return scale

    def _scales(self, fieldname):
        adapter = ICropping(self.context, alternate=None)
        if adapter is None:
            yield from super(SmartwebCroppingEditor, self)._scales(fieldname)
            return
        allowed_sizes = getUtility(IAvailableSizes)() or []
        sizes_iterator = sorted(six.iteritems(allowed_sizes), key=itemgetter(1))
        context_scales = adapter.get_scales(fieldname, self.request)
        for scale_id, target_size in sizes_iterator:
            if scale_id not in context_scales:
                continue
            yield scale_id, target_size


class SmartwebCroppingImageScalingFactory(CroppingImageScalingFactory):
    def __call__(
        self,
        fieldname=None,
        mode="scale",
        height=None,
        width=None,
        scale=None,
        **parameters,
    ):
        storage = Storage(self.context)
        self.box = storage.read(fieldname, scale)
        if scale and ("portrait" in scale or "paysage" in scale or "carre" in scale):
            orientation = scale.split("_")[0]
            # take cropping box from "affiche" scale
            self.box = storage.read(fieldname, f"{orientation}_affiche")
        if self.box:
            mode = "contain"
        else:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ISettings)
            if scale in settings.cropping_for:
                mode = "contain"
        return super(CroppingImageScalingFactory, self).__call__(
            fieldname=fieldname,
            mode=mode,
            height=height,
            width=width,
            scale=scale,
            **parameters,
        )
