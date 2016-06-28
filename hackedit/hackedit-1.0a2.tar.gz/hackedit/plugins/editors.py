"""
This module contains some editor integration plugins for most of the official
pyqode code editors that do not require a specific backend or some specific
settings (rst editor, json editor).
"""
from hackedit import api
from hackedit.app import generic_pyqode_server
from pyqode.rst.widgets import RstCodeEdit
from pyqode.json.widgets import JSONCodeEdit


class RstCodeEditPlugin(api.plugins.EditorPlugin):
    @staticmethod
    def get_editor_class():
        RstCodeEdit.DEFAULT_SERVER = generic_pyqode_server.__file__
        return RstCodeEdit


class JSONCodeEditPlugin(api.plugins.EditorPlugin):
    @staticmethod
    def get_editor_class():
        JSONCodeEdit.DEFAULT_SERVER = generic_pyqode_server.__file__
        return JSONCodeEdit
