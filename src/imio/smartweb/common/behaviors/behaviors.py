from plone.app.contenttypes import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.interfaces import INamedImage
from plone.namedfile.field import NamedBlobImage
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from zope.interface import alsoProvides
from zope.schema import ValidationError
from zope.interface import implementer
from zope.interface import provider


class ICustomLeadImage(ILeadImage):
    pass


class InvalidImageFormat(ValidationError):
    __doc__ = "Unsupported image format."


def validate_image_format(value):
    allowed_extensions = [".gif", ".jpg", ".jpeg", ".png", ".svg", ".webp"]
    if value:
        filename = value.filename.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise InvalidImageFormat
    return True


@implementer(ILeadImage)
@provider(IFormFieldProvider)
class ICustomLeadImageBehavior(ILeadImageBehavior):

    image = NamedBlobImage(
        title=_("label_leadimage", default="Lead Image"),
        description="",
        required=False,
        constraint=validate_image_format,
    )


alsoProvides(ICustomLeadImageBehavior, INamedImage)
