"""
This module contains a plugin that show a terminal in the bottom
area of the window.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqode.core.widgets import Terminal as TerminalWidget

from hackedit import api
from hackedit.app import settings, generic_pyqode_server


class Terminal(api.plugins.WorkspacePlugin):
    """
    Adds a terminal widget that let your run commands from within the IDE.
    """
    def activate(self):
        self.widget = TerminalWidget(parent=api.window.get_main_window(), backend=generic_pyqode_server.__file__)
        dock = api.window.add_dock_widget(self.widget, _('Terminal'), QtGui.QIcon.fromTheme('utilities-terminal'),
                                          QtCore.Qt.BottomDockWidgetArea)
        dock.hide()
        dock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        api.signals.connect_slot(api.signals.CURRENT_PROJECT_CHANGED, self.widget.change_directory)
        self.widget.change_directory(api.project.get_current_project())

    def close(self):
        self.widget.close()

    def apply_preferences(self):
        self.widget.font_name = settings.editor_font()
        self.widget.font_size = settings.editor_font_size()
