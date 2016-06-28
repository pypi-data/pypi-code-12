"""
This plugin adds a new open function to the File menu: Open module
"""
import os

from PyQt5 import QtCore, QtWidgets
from hackedit import api
from rope.base.exceptions import ModuleNotFoundError
from rope.base.fscommands import FileSystemCommands
from rope.base.project import Project


_ = api.gettext.get_translation(package='hackedit-python')


class PyOpenModule(api.plugins.WorkspacePlugin):
    """
    Open python module easiy (Ctrl+Shift+P)
    """
    def activate(self):
        mnu = api.window.get_menu(_('&File'))
        assert isinstance(mnu, QtWidgets.QMenu)
        insert_point = api.window.get_main_window_ui().action_open
        if insert_point:
            action = QtWidgets.QAction(
                api.widgets.FileIconProvider.mimetype_icon('file.py'),
                _('Open python module'), mnu)
            action.setToolTip(_('Quicly open a python module'))
            action.setShortcut(api.shortcuts.get(
                'Open python module', _('Open python module'), 'Ctrl+Alt+O'))
            action.setShortcutContext(QtCore.Qt.WindowShortcut)
            action.triggered.connect(self._open_module)
            mnu.insertAction(insert_point, action)
            api.window.get_main_window().addAction(action)

    def _open_module(self):
        name, status = QtWidgets.QInputDialog.getText(
            self.main_window, _('Open module'), _('Python module:'))
        if status:
            project = Project(api.project.get_current_project(),
                              ropefolder=api.project.FOLDER,
                              fscommands=FileSystemCommands())
            try:
                mod = project.pycore.get_module(name)
            except ModuleNotFoundError:
                mod = None
            if mod:
                resource = mod.get_resource()
                if resource:
                    path = resource.real_path
                    if not os.path.isfile(path):
                        path = os.path.join(path, '__init__.py')
                    if os.path.exists(path):
                        api.editor.open_file(path)
                        return
            QtWidgets.QMessageBox.information(
                self.main_window, _('Module not found'),
                _('Cannot open %r, module not found or not editable...') %
                name)
