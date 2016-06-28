from PyQt5 import QtCore

from hackedit.api import shortcuts


def setup_function(function):
    QtCore.QSettings().clear()
    shortcuts.load()


def test_get_shortcut():
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
    shortcuts.update('My action', 'My action', '')
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'


def test_update_shortcut():
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
    shortcuts.update('My action', 'My action', 'Ctrl+Backspace')
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Backspace'


def test_load_save():
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
    shortcuts.update('My action', 'My action', 'Ctrl+Backspace')
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Backspace'
    shortcuts.load()
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
    shortcuts.update('My action', 'My action', 'Ctrl+Backspace')
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Backspace'
    shortcuts.save()
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Backspace'


def test_get_all_names():
    assert len(shortcuts.get_all_names()) == 0
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
    assert shortcuts.get('My action2', 'My action',
                         'Ctrl+Alt+Return') == 'Ctrl+Alt+Return'
    assert len(shortcuts.get_all_names()) == 2


def test_get_all_texts():
    assert len(shortcuts.get_all_texts()) == 0
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
    assert shortcuts.get('My action2', 'My action',
                         'Ctrl+Alt+Return') == 'Ctrl+Alt+Return'
    assert len(shortcuts.get_all_texts()) == 2


def test_restore_defaults():
    shortcuts.get('My action', 'My action', 'Ctrl+Alt+Delete')
    shortcuts.update('My action', 'My action', 'Ctrl+Backspace')
    shortcuts.save()
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Backspace'
    shortcuts.restore_defaults()
    assert shortcuts.get('My action', 'My action',
                         'Ctrl+Alt+Delete') == 'Ctrl+Alt+Delete'
