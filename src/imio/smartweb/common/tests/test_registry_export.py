# -*- coding: utf-8 -*-

from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from lxml import etree
from plone.app.registry.browser.records import FakeEnv
from plone.app.registry.exportimport.handler import RegistryExporter
from plone.registry.field import TextLine
from plone.registry.interfaces import IInterfaceAwareRecord
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from zope.component import getUtility
from zope.interface import Interface

import unittest


class IDummyIconMarker(Interface):
    """Marker-only interface with no fields, like ISmartwebIcon."""


class TestRegistryExport(unittest.TestCase):
    """The @@registry control panel (and the GenericSetup export step) both
    call RegistryExporter.exportDocument(). Records tagged with a marker
    interface but without a fieldName (e.g. imio.smartweb.core smartweb.icon.*
    records) used to crash the whole export with a lxml TypeError. See the
    monkeypatch in imio.smartweb.common.__init__.
    """

    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.registry = getUtility(IRegistry)

    def _add_marker_record(self, name):
        """Reproduce a smartweb.icon.* style record: a persistent field whose
        interfaceName is set (marker interface) but whose fieldName is None.
        """
        field = TextLine(title="Dummy icon")
        field.interfaceName = IDummyIconMarker.__identifier__
        # field.fieldName is intentionally left as None
        record = Record(field, value="++plone++dummy/icon.svg")
        self.registry.records[name] = record
        return self.registry.records[name]

    def test_marker_record_is_interface_aware_without_fieldname(self):
        record = self._add_marker_record("smartweb.icon.dummy.test")
        self.assertTrue(IInterfaceAwareRecord.providedBy(record))
        self.assertIsNone(record.fieldName)

    def test_export_does_not_crash_on_missing_fieldname(self):
        self._add_marker_record("smartweb.icon.dummy.test")
        exporter = RegistryExporter(self.registry, FakeEnv())
        body = exporter.exportDocument()
        self.assertIn("smartweb.icon.dummy.test", body)

    def test_exported_marker_record_keeps_interface_but_omits_field(self):
        self._add_marker_record("smartweb.icon.dummy.test")
        exporter = RegistryExporter(self.registry, FakeEnv())
        body = exporter.exportDocument()
        tree = etree.fromstring(body.encode("utf-8"))
        nodes = tree.xpath("//record[@name='smartweb.icon.dummy.test']")
        self.assertEqual(len(nodes), 1)
        node = nodes[0]
        self.assertEqual(node.get("interface"), IDummyIconMarker.__identifier__)
        self.assertIsNone(node.get("field"))
        # field element + value are preserved so the record still round-trips
        self.assertEqual(len(node.xpath("./field")), 1)
        self.assertEqual(len(node.xpath("./value")), 1)

    def test_normal_interface_aware_record_still_has_field(self):
        # A properly registered record (interfaceName AND fieldName) must keep
        # exporting its field= attribute: the patch delegates it to upstream.
        field = TextLine(title="Normal")
        field.interfaceName = IDummyIconMarker.__identifier__
        field.fieldName = "normal_field"
        record = Record(field, value="whatever")
        self.registry.records["smartweb.dummy.normal_field"] = record

        exporter = RegistryExporter(self.registry, FakeEnv())
        body = exporter.exportDocument()
        tree = etree.fromstring(body.encode("utf-8"))
        nodes = tree.xpath("//record[@name='smartweb.dummy.normal_field']")
        self.assertEqual(len(nodes), 1)
        node = nodes[0]
        self.assertEqual(node.get("interface"), IDummyIconMarker.__identifier__)
        self.assertEqual(node.get("field"), "normal_field")
