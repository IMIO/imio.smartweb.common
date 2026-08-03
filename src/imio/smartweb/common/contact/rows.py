# -*- coding: utf-8 -*-

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from imio.smartweb.common.widgets.frozen_label import FrozenLabelTextFieldWidget
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.autoform import directives
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import Interface

# Shared by imio.smartweb.core (Section contact) and imio.events.core
# (Secondary contact). The two products disagree on ONE point, deliberately:
# in the section the data columns below are RESIDUE -- the page render re-reads
# the live directory payload and only `visible_columns` is authoritative --
# while in imio.events.core they ARE the published data, because an event has a
# temporality and must show the contact as it was for that event. `type_token`
# exists because of that divergence: see its comment below.


# The identity columns below (`contact_uid`, `type_token`, `contact_title`) are
# repeated verbatim in the three row schemas instead of being factored into a
# shared base interface. That repetition is REQUIRED, not an oversight:
# collective.z3cform.datagridfield's DictRowConverter.toFieldValue iterates
# `self.field.schema.namesAndDescriptions()` WITHOUT `all=True`, so it only ever
# sees an interface's OWN attributes. Inherited columns are silently dropped
# from the converted row, and the value comes back out of storage with those
# keys missing. Do not factor them out again.


class IPhoneDisplayRow(Interface):
    """One phone row of a related contact, plus the columns to display.

    Every column but `visible_columns` is remote directory data rendered as a
    frozen label: read-only looking, yet still submitted, because DictRow
    rejects a row whose keys are missing.
    """

    directives.mode(contact_uid="hidden")
    contact_uid = schema.TextLine(title=_("Contact UID"), required=False)

    # The RAW remote `type` token. The visible `type` column holds the
    # TRANSLATED label, which is what an editor wants to read but which freezes
    # the editor's language into storage. A consumer that publishes the STORED
    # row (imio.events.core) must read this column instead and let its own
    # consumer translate; the section ignores it, since it re-reads the live
    # payload anyway.
    directives.mode(type_token="hidden")
    type_token = schema.TextLine(title=_("Type token"), required=False)

    directives.widget("contact_title", FrozenLabelTextFieldWidget)
    contact_title = schema.TextLine(title=_("Contact"), required=False)

    directives.widget("label", FrozenLabelTextFieldWidget)
    label = schema.TextLine(title=_("Label"), required=False)

    directives.widget("type", FrozenLabelTextFieldWidget)
    type = schema.TextLine(title=_("Type"), required=False)

    directives.widget("number", FrozenLabelTextFieldWidget)
    number = schema.TextLine(title=_("Number"), required=False)

    directives.widget("visible_columns", CheckBoxFieldWidget)
    visible_columns = schema.List(
        title=_("Displayed columns"),
        value_type=schema.Choice(
            vocabulary="imio.smartweb.vocabulary.PhoneDisplayColumns"
        ),
        required=False,
    )


class IMailDisplayRow(Interface):
    """One e-mail row of a related contact, plus the columns to display.

    See IPhoneDisplayRow for why the identity columns are repeated here.
    """

    directives.mode(contact_uid="hidden")
    contact_uid = schema.TextLine(title=_("Contact UID"), required=False)

    directives.mode(type_token="hidden")
    type_token = schema.TextLine(title=_("Type token"), required=False)

    directives.widget("contact_title", FrozenLabelTextFieldWidget)
    contact_title = schema.TextLine(title=_("Contact"), required=False)

    directives.widget("label", FrozenLabelTextFieldWidget)
    label = schema.TextLine(title=_("Label"), required=False)

    directives.widget("type", FrozenLabelTextFieldWidget)
    type = schema.TextLine(title=_("Type"), required=False)

    directives.widget("mail_address", FrozenLabelTextFieldWidget)
    mail_address = schema.TextLine(title=_("E-mail"), required=False)

    directives.widget("visible_columns", CheckBoxFieldWidget)
    visible_columns = schema.List(
        title=_("Displayed columns"),
        value_type=schema.Choice(
            vocabulary="imio.smartweb.vocabulary.MailDisplayColumns"
        ),
        required=False,
    )


class IUrlDisplayRow(Interface):
    """One URL row of a related contact, plus the columns to display.

    See IPhoneDisplayRow for why the identity columns are repeated here.
    """

    directives.mode(contact_uid="hidden")
    contact_uid = schema.TextLine(title=_("Contact UID"), required=False)

    directives.mode(type_token="hidden")
    type_token = schema.TextLine(title=_("Type token"), required=False)

    directives.widget("contact_title", FrozenLabelTextFieldWidget)
    contact_title = schema.TextLine(title=_("Contact"), required=False)

    directives.widget("type", FrozenLabelTextFieldWidget)
    type = schema.TextLine(title=_("Type"), required=False)

    directives.widget("url", FrozenLabelTextFieldWidget)
    url = schema.TextLine(title=_("Url"), required=False)

    directives.widget("visible_columns", CheckBoxFieldWidget)
    visible_columns = schema.List(
        title=_("Displayed columns"),
        value_type=schema.Choice(
            vocabulary="imio.smartweb.vocabulary.UrlDisplayColumns"
        ),
        required=False,
    )


class IContactInformationsGrids(model.Schema):
    """The three read-only contact-informations datagrids.

    Inherited by ISectionContact (imio.smartweb.core) and ISecondaryContact
    (imio.events.core) so the declarations exist once. The field descriptions
    keep their original plural wording so the translations already authored in
    imio.smartweb.locales stay valid.
    """

    model.fieldset(
        "contact_informations",
        label=_("Contact informations"),
        fields=["phones_display", "mails_display", "urls_display"],
    )

    directives.widget(
        "phones_display",
        DataGridFieldFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=False,
    )
    phones_display = schema.List(
        title=_("Phones"),
        description=_(
            "Read-only rows loaded from the related contacts with the button "
            "at the bottom of this form. Check the columns you want to "
            "display; uncheck them all to hide the row."
        ),
        value_type=DictRow(title="Value", schema=IPhoneDisplayRow),
        required=False,
    )

    directives.widget(
        "mails_display",
        DataGridFieldFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=False,
    )
    mails_display = schema.List(
        title=_("E-mails"),
        description=_(
            "Read-only rows loaded from the related contacts with the button "
            "at the bottom of this form. Check the columns you want to "
            "display; uncheck them all to hide the row."
        ),
        value_type=DictRow(title="Value", schema=IMailDisplayRow),
        required=False,
    )

    directives.widget(
        "urls_display",
        DataGridFieldFactory,
        allow_insert=False,
        allow_delete=False,
        allow_reorder=False,
        auto_append=False,
    )
    urls_display = schema.List(
        title=_("URLs"),
        description=_(
            "Read-only rows loaded from the related contacts with the button "
            "at the bottom of this form. Check the columns you want to "
            "display; uncheck them all to hide the row."
        ),
        value_type=DictRow(title="Value", schema=IUrlDisplayRow),
        required=False,
    )
