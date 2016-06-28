import os
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqode.core.widgets import FileSystemTreeView

import pytest_hackedit

from hackedit.api import editor, window


DATA_FILES_PATH = os.path.join(os.getcwd(), 'tests', 'data')
PROJ_PATH = os.path.join(DATA_FILES_PATH, 'FooBarProj')
FILE1 = os.path.join(PROJ_PATH, 'module.py')
FILE2 = os.path.join(PROJ_PATH, 'setup.py')
PATH2 = os.path.join(DATA_FILES_PATH, 'SpamEggsProj')


def test_add_tab_widget_context_menu_action():
    with pytest_hackedit.MainWindow(PROJ_PATH) as w:
        window.add_tab_widget_context_menu_action(
            QtWidgets.QAction('Test', w.instance))


def test_get_tab_under_context_menu():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        assert window.get_tab_under_context_menu() is None


def test_add_dock_widget():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        dw = window.add_dock_widget(
            QtWidgets.QPushButton(), 'FooDock',
            QtGui.QIcon.fromTheme('document-save'),
            QtCore.Qt.BottomDockWidgetArea)
        assert dw is not None
        assert isinstance(dw, QtWidgets.QDockWidget)


def test_remove_dock_widget():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        dw = window.add_dock_widget(
            QtWidgets.QPushButton(), 'FooDock2',
            QtGui.QIcon.fromTheme('document-save'),
            QtCore.Qt.BottomDockWidgetArea)
        window.remove_dock_widget(dw)


def test_get_dock_widget():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        dw = window.add_dock_widget(
            QtWidgets.QPushButton(), 'FooDock',
            QtGui.QIcon.fromTheme('document-save'),
            QtCore.Qt.BottomDockWidgetArea)
        ret_val = window.get_dock_widget('FooDock')
        assert ret_val == dw


def test_get_main_window():
    with pytest_hackedit.MainWindow(PROJ_PATH) as w:
        assert w.instance == window.get_main_window()


def test_get_toolbar():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        tb = window.get_toolbar('toolBarFile', 'FileToolBar')
        assert isinstance(tb, QtWidgets.QToolBar)


def test_add__action():
    with pytest_hackedit.MainWindow(PROJ_PATH) as w:
        window.add_action(QtWidgets.QAction('Test', w.instance))


def test_get_menu():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        mnu = window.get_menu(_('Edit'))
        assert mnu is not None
        assert isinstance(mnu, QtWidgets.QMenu)


def test_get_project_treeview():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        assert isinstance(window.get_project_treeview(), FileSystemTreeView)


def test_add_statusbar_widget():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        lbl = QtWidgets.QLabel()
        window.add_statusbar_widget(lbl)
