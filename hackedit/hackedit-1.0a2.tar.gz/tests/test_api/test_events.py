from PyQt5 import QtCore, QtTest, QtWidgets

import pytest_hackedit
from hackedit.api import events, window

from .test_window import PROJ_PATH


def test_create_event():
    # test with default args
    e = events.Event('title', 'description')
    assert e.title == 'title'
    assert e.description == 'description'
    assert e.level == events.INFO
    assert len(e.custom_actions) == 0
    assert e.main_window is None
    assert e.time_str != ''
    assert e.action_blacklist is not None
    assert len(e.actions) == 1

    # test with overriden keyworded args
    e = events.Event('title', 'description', level=events.WARNING,
                     custom_actions=[QtWidgets.QAction('test', None)])
    assert e.title == 'title'
    assert e.description == 'description'
    assert e.level == events.WARNING
    assert len(e.custom_actions) == 1
    assert e.main_window is None
    assert e.time_str != ''
    assert e.action_blacklist is not None
    assert len(e.actions) == 2


def test_blacklist():
    e = events.Event('BlackListed', 'BlackListed event')
    assert events.is_blacklisted(e) is False
    e._blacklist_event()
    assert events.is_blacklisted(e) is True
    events.clear_blacklist()
    assert events.is_blacklisted(e) is False
    e._blacklist_event()
    assert events.is_blacklisted(e) is True
    assert len(events.get_blacklist()) == 1
    events.set_blacklist([])
    assert events.is_blacklisted(e) is False
    assert len(events.get_blacklist()) == 0


def cancel_dialog():
    for dlg in window.get_main_window().findChildren(QtWidgets.QDialog):
        dlg.reject()


def test_exception_event():
    with pytest_hackedit.MainWindow(PROJ_PATH) as w:
        try:
            print(10/0)
        except Exception as e:
            e = events.ExceptionEvent("Unhandled exception", str(e), e)
            assert e.traceback != ''
            assert len(e.custom_actions) == 2
            events.post(e, show_balloon=True, force_show=True)
            events.post(e)
            assert e.main_window == w.instance

            QtCore.QTimer.singleShot(1000, cancel_dialog)
            e.show_details()

            QtCore.QTimer.singleShot(1000, cancel_dialog)
            e.report_bug()


def test_plugin_load_error_event():
    with pytest_hackedit.MainWindow(PROJ_PATH) as w:
        try:
            print(10/0)
        except Exception as e:
            e = events.PluginLoadErrorEvent("Unhandled exception", str(e), e)
            assert e.traceback != ''
            assert len(e.custom_actions) == 2
            events.post(e, show_balloon=True, force_show=True)
            events.post(e)
            assert e.main_window == w.instance

            QtCore.QTimer.singleShot(1000, cancel_dialog)
            e.report_bug()
