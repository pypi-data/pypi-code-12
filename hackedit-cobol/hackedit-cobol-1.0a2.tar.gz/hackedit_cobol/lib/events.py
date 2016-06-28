import os

from PyQt5 import QtWidgets
from hackedit import api

from hackedit_cobol.lib.compiler import GnuCOBOLCompiler, MODULE


_ = api.gettext.get_translation(package='hackedit-cobol')


class FileNotInProjectEvent(api.events.Event):
    def __init__(self, path, project, project_manager):
        self._manager = project_manager
        self._path = path
        self._project = project
        self.action_add = QtWidgets.QAction(
            _('Add to project'), None)
        self.action_add.triggered.connect(self.add)
        actions = [self.action_add]
        super().__init__(
            _('File not in project configuration!'),
            _('The file "%s" has not been added to the project '
              'configuration.\n\nWould you like to add it now?\n') % path,
            level=api.events.WARNING, custom_actions=actions)

    def add(self):
        from hackedit_cobol.plugins.project_mode import DlgConfigureProject, \
            get_project_config, set_project_config
        ftype = GnuCOBOLCompiler.get_file_type(self._path)
        if ftype == MODULE:
            cfg = DlgConfigureProject.DEFAULT_MODULE_CFG
        else:
            cfg = DlgConfigureProject.DEFAULT_EXECUTABLE_CFG
        cfg['path'] = os.path.relpath(self._path, self._project)
        prj_cfg = get_project_config(self._project)
        prj_cfg.append(cfg)
        set_project_config(self._project, prj_cfg)
        self.remove()
        self._manager.configuration_changed.emit()
