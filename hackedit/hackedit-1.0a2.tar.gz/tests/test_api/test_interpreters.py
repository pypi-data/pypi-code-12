import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqode.core.widgets import OutputWindow

from hackedit.api import project
from hackedit.api.interpreters import (
    InterpreterManager, ScriptRunnerPlugin, create_default_config,
    save_configs, load_configs, get_active_config_name, save_active_config)
import pytest_hackedit

DATA_FILES_PATH = os.path.join(os.getcwd(), 'tests', 'data')
PROJ_PATH = os.path.join(DATA_FILES_PATH, 'SpamEggsProj')


class PythonManager(InterpreterManager):
    def __init__(self):
        super().__init__('python', default_interpreter=sys.executable,
                         mimetype='text/x-python')

    def _detect_system_interpreters(self):
        return ['/usr/bin/python', sys.executable]


class BrokenManager(InterpreterManager):
    def __init__(self):
        super().__init__('python', default_interpreter='/usr/bin/python39')

    def _detect_system_interpreters(self):
        return []


class TestInterpreterManager:
    @classmethod
    def setup(cls):
        QtCore.QSettings().clear()
        try:
            os.remove(os.path.join(PROJ_PATH, project.FOLDER, 'config.usr'))
        except OSError:
            pass

    def test_extensions(self):
        assert len(PythonManager().extensions)

    def test_icon(self):
        icon = PythonManager().get_interpreter_icon()
        assert isinstance(icon, QtGui.QIcon)

    def test_all_interpreters(self):
        assert len(PythonManager().all_interpreters) == 2

    def test_default_interpreter(self):
        assert PythonManager().default_interpreter == sys.executable
        PythonManager().default_interpreter = '/usr/bin/python2.7'
        assert PythonManager().default_interpreter == '/usr/bin/python2.7'

    def test_boken_default_interpreter(self):
        assert BrokenManager().default_interpreter == ''

    def test_add_interpreter(self):
        assert len(PythonManager().all_interpreters) == 2
        if sys.platform == 'win32':
            PythonManager().add_interpreter('C:\\Python27\python.exe')
        else:
            PythonManager().add_interpreter('/usr/bin/python2.7')
        assert len(PythonManager().all_interpreters) == 3

    def test_rm_interpreter(self):
        assert len(PythonManager().all_interpreters) == 2
        if sys.platform == 'win32':
            PythonManager().add_interpreter('C:\\Python27\python.exe')
        else:
            PythonManager().add_interpreter('/usr/bin/python2.7')
        assert len(PythonManager().all_interpreters) == 3
        if sys.platform == 'win32':
            PythonManager().remove_interpreter('C:\\Python27\python.exe')
        else:
            PythonManager().remove_interpreter('/usr/bin/python2.7')
        assert len(PythonManager().all_interpreters) == 2
        # cannot remove a system interpreter
        PythonManager().remove_interpreter('/usr/bin/python')
        assert len(PythonManager().all_interpreters) == 2

    def test_prj_interpreter(self):
        pm = PythonManager()
        assert pm.get_project_interpreter(PROJ_PATH) == pm.default_interpreter
        pm.set_project_interpreter(PROJ_PATH, sys.executable)
        assert pm.get_project_interpreter(PROJ_PATH) == sys.executable

    def test_detect_interpreters(self):
        assert InterpreterManager('test')._detect_system_interpreters() == []


class FakeScriptRunnerPlugin(ScriptRunnerPlugin):
    def __init__(self, window):
        super().__init__(window, PythonManager(), OutputWindow)


def test_scriptrunnerplugin(qtbot):
    def click_cancel():
        qtbot.keyPress(QtWidgets.qApp.activeWindow(), QtCore.Qt.Key_Escape)

    # not really a unit test, kinda functional
    with pytest_hackedit.MainWindow(PROJ_PATH) as w:
        p = FakeScriptRunnerPlugin(w.instance)
        p.enable_mnu_configs()
        p.enable_run()


def test_create_default_config():
    cfg = create_default_config(PROJ_PATH)
    assert not cfg['script']
    cfg = create_default_config(os.path.join(PROJ_PATH, 'module.py'))
    assert cfg['script']


def test_save_configs():
    cfg = create_default_config(os.path.join(PROJ_PATH, 'module.py'))
    save_configs(PROJ_PATH, [cfg, create_default_config(PROJ_PATH)])


def test_load_configs():
    assert len(load_configs(PROJ_PATH)) == 2


def test_active_config():
    active = get_active_config_name(PROJ_PATH, load_configs(PROJ_PATH))
    assert active == 'Unnamed'
    save_active_config(PROJ_PATH, 'module')
    active = get_active_config_name(PROJ_PATH, load_configs(PROJ_PATH))
    assert active == 'module'
