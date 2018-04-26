# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import

__author__ = 'renken@marum.de'
__date__ = '2015-06-01'
__copyright__ = 'Copyright 2015, Jens Renken/Marum/University of Bremen'

import unittest

from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog

from gui.posiview_properties import PosiviewProperties
from posiview_project import PosiViewProject

from .utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class PosiViewDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        proj = PosiViewProject({})
        self.dialog = PosiviewProperties(proj, None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.buttonBox.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.buttonBox.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

    def test_dialog_apply(self):
        """Test we can click apply."""
        button = self.dialog.buttonBox.button(QDialogButtonBox.Apply)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)


if __name__ == "__main__":
    suite = unittest.makeSuite(PosiViewDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
