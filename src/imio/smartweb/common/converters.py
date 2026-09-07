# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import ITranslatedAjaxSelectWidget
from z3c.form.converter import BaseDataConverter
from zope.component import adapter
from zope.schema.interfaces import IChoice


@adapter(IChoice, ITranslatedAjaxSelectWidget)
class AjaxSelectChoiceDataConverter(BaseDataConverter):
    """Data converter for a single-valued Choice on an ajax select widget.

    plone.app.z3cform only registers its AjaxSelectWidgetConverter for
    ICollection fields, so a plain Choice fell back to z3c.form's
    FieldDataConverter, which calls ``Choice.fromUnicode()`` on the **unbound**
    schema field. An unbound Choice resolves its named vocabulary against a
    ``None`` context, and a context-aware factory such as
    ``imio.smartweb.vocabulary.RemoteDirectoryContact`` (which needs the parent
    Entity to know the linked directory entities) can only answer that with an
    empty vocabulary: every value was rejected with ConstraintNotSatisfied, so
    a field such as ``directory_linked_contact`` could never be saved with a
    contact selected.

    Resolving the token through ``widget.get_vocabulary()`` -- the vocabulary
    built for the content being edited -- is what AjaxSelectWidgetConverter
    already does for multi-valued siblings.

    ``toWidgetValue`` is left to BaseDataConverter on purpose: it keeps the
    rendering exactly as it was, and the widget's own ``display_items()``
    already resolves the token to its title, so there is no reason to pay for a
    second remote call per form render.
    """

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        self.widget.update()  # needed to have a vocabulary
        vocabulary = self.widget.get_vocabulary()
        if vocabulary is not None:
            try:
                return vocabulary.getTermByToken(value).value
            except (LookupError, ValueError):
                pass
        # Unknown token: hand it over as it came. z3c.form validates the
        # extracted value right after with the field bound to the content being
        # edited, which is where an out-of-scope value gets its proper
        # ConstraintNotSatisfied on the widget.
        return value
