from plone.namedfile.scaling import NavigationRootScaling as BaseNavigationRootScaling
from zope.cachedescriptors.property import Lazy as lazy_property


class NavigationRootScaling(BaseNavigationRootScaling):
    @lazy_property
    def _supports_image_scales_metadata(self):
        return False
