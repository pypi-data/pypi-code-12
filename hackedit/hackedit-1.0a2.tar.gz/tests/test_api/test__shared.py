import os
from hackedit.api import _shared
from hackedit.app.main_window import MainWindow
from hackedit.plugins.workspaces import GenericWorkspace

import pytest_hackedit


DATA_FILES_PATH = os.path.join(os.getcwd(), 'tests', 'data')
PROJ_PATH = os.path.join(DATA_FILES_PATH, 'FooBarProj')


class NoWindow:
    def get_window(self):
        return _shared._window()


class NoneWindow:
    def __init__(self):
        self.main_window = None

    def get_window(self):
        return self._get()

    def _get(self):
        w = _shared._window()
        return w


class WrongType:
    def __init__(self):
        self.main_window = 10

    def get_window(self):
        return self._get()

    def _get(self):
        w = _shared._window()
        return w


class CorrectType:
    def __init__(self):
        self.main_window = MainWindow(pytest_hackedit.app(), PROJ_PATH,
                                      GenericWorkspace.get_data())

    def get_window(self):
        return self._get()

    def _get(self):
        w = _shared._window()
        return w


def test_no_window(qtbot):
    pytest_hackedit.app()
    assert NoWindow().get_window() is None


def test_none_window():
    pytest_hackedit.app()
    w = NoneWindow().get_window()
    assert w is None


def test_wrong_type():
    pytest_hackedit.app()
    w = WrongType().get_window()
    assert w is None


def test_correct_type():
    pytest_hackedit.app()
    w = CorrectType().get_window()
    assert w is not None
    assert isinstance(w, MainWindow)
    w.close()
