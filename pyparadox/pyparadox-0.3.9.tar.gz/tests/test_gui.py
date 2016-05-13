# -*- coding: utf-8 -*-
#
# PyParadox is a nix launcher for Paradox titles.
# Copyright (C) 2014  Carmen Bianca Bakker <carmenbbakker@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from unittest import mock
from unittest.mock import patch

from PyQt5 import QtWidgets
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from pyparadox import gui


class TestMainWindow(unittest.TestCase):

    @patch('pyparadox.gui.LogicWrapper')
    def setUp(self, gui_LogicWrapper):
        self.app = QtWidgets.QApplication([])
        self.config = mock.MagicMock()
        self.form = gui.MainWindow(self.config)
        # Does not verify whether only legal LogicWrapper methods are called.
        # Autospeccing results in problems with Qt slots and signals.
        self.assertTrue(self.form._logicWrapper.resetModels.called)
        self.form._logicWrapper.reset_mock()

    def test_on_runBtn_clicked(self):
        logicWrapper = self.form._logicWrapper
        QTest.mouseClick(self.form.runBtn, Qt.LeftButton)
        self.assertTrue(logicWrapper.savePlugins.called)
        self.assertTrue(logicWrapper.run.called)

    @patch('pyparadox.gui.ConfigDlg')
    def test_on_configBtn_clicked_no_save(self, gui_ConfigDlg):
        configDlg = gui_ConfigDlg()
        configDlg.exec_.return_value = False
        QTest.mouseClick(self.form.configBtn, Qt.LeftButton)
        self.assertTrue(configDlg.exec_.called)
        self.assertFalse(self.form._logicWrapper.savePlugins.called)
        self.assertFalse(self.form._logicWrapper.resetModels.called)

    @patch('pyparadox.gui.ConfigDlg')
    def test_on_configBtn_clicked_save(self, gui_ConfigDlg):
        configDlg = gui_ConfigDlg()
        configDlg.exec_.return_value = True
        configDlg.binaryPathEdit.text.return_value = "foo"
        configDlg.modPathEdit.text.return_value = "bar"
        QTest.mouseClick(self.form.configBtn, Qt.LeftButton)
        self.assertTrue(configDlg.exec_.called)
        self.form._config.__setitem__.assert_any_call("binary_path", "foo")
        self.form._config.__setitem__.assert_any_call("mod_path", "bar")
        self.assertTrue(self.form._logicWrapper.savePlugins.called)
        self.assertTrue(self.form._logicWrapper.resetModels.called)


class TestMainWindowSlots(unittest.TestCase):

    @patch('pyparadox.gui.find_plugins')
    def setUp(self, gui_find_plugins):
        self.app = QtWidgets.QApplication([])
        self.config = mock.MagicMock()
        self.form = gui.MainWindow(self.config)

    @patch('pyparadox.gui.QtWidgets.QMessageBox', autospec=True)
    def test_runFailed(self, gui_QMessageBox):
        self.form._logicWrapper.runFailed.emit("foo", "bar")
        self.assertTrue(gui_QMessageBox.called)
        msgBox = gui_QMessageBox()
        self.assertTrue(msgBox.exec_.called)

    def test_runSucceeded(self):
        self.form._logicWrapper.runSucceeded.emit()
        # TODO: Figure out how to detect whether the window was successfully
        # closed.
