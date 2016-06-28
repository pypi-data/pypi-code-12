"""
This module contains a plugin that show a terminal in the bottom
area of the window.
"""
from PyQt5 import QtCore, QtWidgets

from pyqode.core.api import ColorScheme
from pyqode.python.widgets import PyConsole as PyConsoleWidget

from hackedit import api
from hackedit.app import settings

from . import pyqode_server
from .interpreters import PythonManager


class PyConsole(api.plugins.WorkspacePlugin):
    """
    Adds a python console widget to the IDE.
    """
    def activate(self):
        self.widget = PyConsoleWidget(parent=api.window.get_main_window(), color_scheme=settings.color_scheme(),
                                      backend=pyqode_server.__file__)
        dock = api.window.add_dock_widget(self.widget, _('Python Console'),
                                          PythonManager.get_interpreter_icon(), QtCore.Qt.BottomDockWidgetArea)
        dock.hide()
        dock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.script_runner = api.plugins.get_script_runner()
        self.script_runner.config_refreshed.connect(self._update_interpreter)
        self._interpeter = None
        self._update_interpreter()

    def close(self):
        self.widget.close()

    def apply_preferences(self):
        self.widget.font_name = settings.editor_font()
        self.widget.font_size = settings.editor_font_size()
        self.widget.syntax_highlighter.color_scheme = ColorScheme(settings.color_scheme())
        self.widget.update_terminal_colors()

    def _update_interpreter(self):
        interpeter = PythonManager().get_project_interpreter(api.project.get_current_project())
        if interpeter != self._interpeter:
            self.widget.change_interpreter(interpeter)
            self._interpeter = interpeter
