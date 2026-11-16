# -*- coding: utf-8 -*-

from DateTime import DateTime
from freezegun import freeze_time
from imio.smartweb.common.testing import IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from unittest.mock import MagicMock
from unittest.mock import patch
from ZODB.POSException import ConflictError

import unittest


class TestDescription(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    @freeze_time("2023-12-14 9:00:00")
    def test_added_content_image(self):
        # content types for which effective date is equal to created date (thank to subrscriber)
        content_types = ["File", "Image"]
        frozen_time = DateTime()

        for ct in content_types:
            obj = api.content.create(
                container=self.portal,
                type=ct,
                title=f"My {ct}",
            )
            if IFile.providedBy(obj):
                obj.file = NamedBlobFile(data="file data", filename="file.txt")

            elif IImage.providedBy(obj):
                obj.image = NamedBlobImage(data="file data", filename="file.txt")

            self.assertEqual(obj.effective(), frozen_time)
            # subscriber added_content fix effective as created date for Image content type
            self.assertEqual(obj.effective(), obj.created())


class TestStartedZope(unittest.TestCase):
    layer = IMIO_SMARTWEB_COMMON_INTEGRATION_TESTING

    def _connection(self, app):
        conn = MagicMock()
        conn.root.return_value = {"Application": app}
        return conn

    def _started_zope(self, conn, commit_error=None):
        from imio.smartweb.common import subscribers

        with patch.object(subscribers, "Zope2") as mock_zope2, patch.object(
            subscribers, "setSite"
        ) as mock_set_site, patch.object(
            subscribers, "queryUtility", return_value=MagicMock()
        ), patch.object(
            subscribers, "update_resource_registry_mtime"
        ) as mock_update, patch.object(
            subscribers, "transaction"
        ) as mock_transaction:
            mock_zope2.DB.open.return_value = conn
            if commit_error is not None:
                mock_transaction.commit.side_effect = commit_error
            subscribers.started_zope(None)
        return mock_set_site, mock_update, mock_transaction

    def test_connection_closed_when_site_missing(self):
        """Without a Plone site, the connection must still be closed: a leaked
        one keeps its storage read snapshot open (idle in transaction)."""
        app = MagicMock()
        app.unrestrictedTraverse.side_effect = KeyError("Plone")
        conn = self._connection(app)
        mock_set_site, mock_update, mock_transaction = self._started_zope(conn)
        mock_update.assert_not_called()
        mock_transaction.commit.assert_not_called()
        mock_transaction.abort.assert_called_once()
        conn.close.assert_called_once()

    def test_mtime_committed_and_connection_closed(self):
        """The resource registry mtime update is committed, so the
        resourceRegistries ETag changes at each restart, then the site is
        unset and the connection closed."""
        site = object()
        app = MagicMock()
        app.unrestrictedTraverse.return_value = site
        conn = self._connection(app)
        mock_set_site, mock_update, mock_transaction = self._started_zope(conn)
        mock_update.assert_called_once()
        mock_transaction.commit.assert_called_once()
        assert [c.args for c in mock_set_site.call_args_list] == [(site,), (None,)]
        mock_transaction.abort.assert_called_once()
        conn.close.assert_called_once()

    def test_conflict_does_not_break_startup(self):
        """Another process of the same site may update the mtime at the same
        time: the conflict is ignored and the connection still closed."""
        app = MagicMock()
        app.unrestrictedTraverse.return_value = object()
        conn = self._connection(app)
        mock_set_site, mock_update, mock_transaction = self._started_zope(
            conn, commit_error=ConflictError()
        )
        mock_transaction.commit.assert_called_once()
        mock_transaction.abort.assert_called_once()
        conn.close.assert_called_once()
