from PyQt5 import QtWidgets

from hackedit.api import utils
from hackedit.app import mime_types, settings


def test_add_mimetype_extension():
    settings.load()
    settings._SETTINGS.clear()
    mtype = 'text/x-own'
    ext = '.own'
    assert ext not in mime_types.get_extensions(mtype)
    utils.add_mimetype_extension(mtype, ext)
    assert ext in mime_types.get_extensions(mtype)


def test_get_mimetype_filter():
    ret = utils.get_mimetype_filter('text/x-python')
    assert 'text/x-python (*.py *.pyw ' in ret


def test_get_ignored_patterns():
    patterns = utils.get_ignored_patterns()
    assert len(patterns) > 1


def test_get_cmd_open_folder_in_terminal():
    cmd = utils.get_cmd_open_folder_in_terminal()
    assert cmd != ''


def test_get_cmd_run_command_in_terminal():
    cmd = utils.get_cmd_run_command_in_terminal()
    assert cmd != ''


def test_get_cmd_open_in_explorer():
    cmd = utils.get_cmd_open_in_explorer()
    assert cmd != ''


def test_get_color_scheme():
    scheme = utils.color_scheme()
    assert isinstance(scheme, str)
    assert scheme in ['aube', 'crepuscule']


def test_is_dark_color_scheme():
    assert utils.is_dark_color_scheme('aube') is False
    assert utils.is_dark_color_scheme('crepuscule') is True


def test_editor_font():
    assert utils.editor_font() == 'Hack'


def test_editor_font_size():
    assert utils.editor_font_size() == 10


toggled = False


def on_toggle():
    global toggled
    toggled = True


def test_block_signal(qtbot):
    checkbox = QtWidgets.QCheckBox()
    checkbox.toggled.connect(on_toggle)
    with utils.block_signals(checkbox):
        checkbox.toggle()
    assert toggled is False
    checkbox.toggle()
    assert toggled is True


def test_is_ignored_path():
    assert utils.is_ignored_path('file.pyc') is True
    assert utils.is_ignored_path('file.py') is False
