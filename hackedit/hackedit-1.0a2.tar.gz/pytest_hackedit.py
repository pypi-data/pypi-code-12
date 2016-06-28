"""
This module contains a bunch of utility functions for testing HackEdit (and its
plugins). This module is part of the hackedit distribution. To use it, just
import pytest_hackedit and use one of the available functions.
"""
import os
import shutil
import sys

from PyQt5 import QtCore, QtWidgets, QtTest

from hackedit.api import project
from hackedit.app import settings


APP = None


class MainWindow:
    """
    Context manager that creates a new editor window and automatically
    close it when exitting the context.

    :attr:`instance` is a reference to the created main window.

    Example::

        import pytest_hackedit
        from hackedit.app.main_window import MainWindow

        with pytest_hackedit.MainWindow('/path/to/project') as w:
            assert isinstance(w.instance, MainWindow)

    """
    def __init__(self, path, remove_project_folder=False):
        self._path = path
        self._remove_project_folder = remove_project_folder
        #: instance of the MainWindow
        self.instance = None

    def __enter__(self):
        if self._remove_project_folder:
            try:
                shutil.rmtree(os.path.join(self._path, project.FOLDER))
            except OSError:
                pass
        a = app()
        a.show_windows = False
        settings.load()
        QtCore.QSettings().clear()
        settings.set_confirm_app_exit(False)
        a.open_path(self._path)
        self.instance = a.editor_windows[-1]
        return self

    def __exit__(self, *args):
        self.instance.close()
        self.instance = None


def app():
    """
    Get the hackedit application instance.
    """
    from hackedit.app.application import Application
    from hackedit.app import argparser
    global APP
    if APP is None:
        sys.argv = [sys.argv[0]]
        APP = Application(QtWidgets.qApp, None, args=argparser.parse_args())
    return APP
