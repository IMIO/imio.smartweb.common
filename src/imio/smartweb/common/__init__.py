# -*- coding: utf-8 -*-

from Acquisition import aq_base
from lxml import etree
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.dexterity.textindexer.utils import searchable
from plone.app.registry.exportimport.handler import RegistryExporter
from plone.registry.interfaces import IFieldRef
from plone.registry.interfaces import IInterfaceAwareRecord
from plone.resource.file import FilesystemFile
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.utils import valueToElement
from Products.CMFPlone.resources import utils
from Products.CMFPlone.resources import webresource
from Products.CMFPlone.resources.utils import get_override_directory
from Products.CMFPlone.resources.utils import logger
from zExceptions import NotFound
from zope.component import queryUtility

searchable(ICategorization, "subjects")


def patched_get_resource(context, path):
    """
    Avoid errors with TTW theme resources
    See https://github.com/plone/Products.CMFPlone/issues/3705
    """
    if path.startswith("++plone++"):
        # ++plone++ resources can be customized, we return their override
        # value if any
        overrides = get_override_directory(context)
        filepath = path[9:]
        if overrides.isFile(filepath):
            return overrides.readFile(filepath)

    if "?" in path:
        # Example from plone.session:
        # "acl_users/session/refresh?session_refresh=true&type=css&minutes=5"
        # Traversing will not work then.  In this example we could split on "?"
        # and traverse to the first part, acl_users/session/refresh, but this
        # gives a function, and this fails when we call it below, missing a
        # REQUEST argument
        return
    try:
        resource = context.unrestrictedTraverse(path)
    except (NotFound, AttributeError, KeyError):
        logger.warning(
            f"Could not find resource {path}. You may have to create it first."
        )  # noqa
        return

    if isinstance(resource, FilesystemFile):
        directory, sep, filename = path.rpartition("/")
        return context.unrestrictedTraverse(directory).readFile(filename)

    # calling the resource may modify the header, i.e. the content-type.
    # we do not want this, so keep the original header intact.
    response_before = context.REQUEST.response
    context.REQUEST.response = response_before.__class__()
    if hasattr(aq_base(resource), "GET"):
        # for FileResource
        result = resource.GET()
    else:
        # any BrowserView
        try:
            # MONKEY IMIO: this avoids AttributeError: __call__ on resources
            result = resource()
        except AttributeError:
            if isinstance(resource.data, bytes):
                result = resource.data
            elif isinstance(resource.data.data, bytes):
                result = resource.data.data
    context.REQUEST.response = response_before
    return result


utils.get_resource = patched_get_resource
webresource.get_resource = patched_get_resource


_original_export_record = RegistryExporter.exportRecord


def patched_export_record(self, record):
    """Avoid crashing the whole registry export on interface-aware records
    that have no fieldName.

    A record is flagged IInterfaceAwareRecord as soon as its field carries an
    ``interfaceName`` (plone.registry.record.Record). Some records are tagged
    with a *marker* interface only (no matching field), so their ``fieldName``
    stays None -- e.g. the imio.smartweb.core ``smartweb.icon.*`` records that
    use the ISmartwebIcon marker to be discoverable in the icons vocabulary.

    Upstream RegistryExporter.exportRecord unconditionally does
    ``node.attrib["field"] = record.fieldName``; with fieldName None lxml
    raises ``TypeError: Argument must be bytes or unicode, got 'NoneType'``,
    which aborts the export of the *entire* configuration registry (control
    panel "Export" button and the GenericSetup registry export step).

    Normal records are delegated untouched to the upstream implementation.
    For the problematic ones we reproduce the upstream output but omit the
    invalid ``field=`` attribute; the inline <field> element and <value> are
    kept, so the record still round-trips on import (it comes back with
    interfaceName set and fieldName None, exactly like today).
    """
    if not (IInterfaceAwareRecord.providedBy(record) and record.fieldName is None):
        return _original_export_record(self, record)

    node = etree.Element("record")
    node.attrib["name"] = record.__name__
    if record.interfaceName is not None:
        node.attrib["interface"] = record.interfaceName
    # NOTE: "field" attribute intentionally omitted (record.fieldName is None)

    # write field (mirrors upstream exportRecord)
    field = record.field
    if IFieldRef.providedBy(field):
        field_element = etree.Element("field")
        field_element.attrib["ref"] = field.recordName
        node.append(field_element)
    else:
        field_type = IFieldNameExtractor(record.field)()
        handler = queryUtility(IFieldExportImportHandler, name=field_type)
        if handler is None:
            self.logger.warning(
                "Field type {} specified for record {} "
                "cannot be exported".format(field_type, record.__name__)
            )
        else:
            field_element = handler.write(
                record.field, None, field_type, elementName="field"
            )
            node.append(field_element)

    # write value
    value_element = valueToElement(record.field, record.value, name="value", force=True)
    node.append(value_element)

    return node


RegistryExporter.exportRecord = patched_export_record
