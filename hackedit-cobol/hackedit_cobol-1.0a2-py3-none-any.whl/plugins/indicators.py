from PyQt5 import QtWidgets

from hackedit import api
from hackedit_cobol.plugins.editor import CobolEditor
from hackedit_cobol.plugins.project_mode import (
    find_file_config, get_project_config, set_project_config,
    CobProjectManager)
from hackedit_cobol.plugins.file_mode import (
    get_file_config, set_file_config, CobFileManager)


class CobFileIndicators(api.plugins.WorkspacePlugin):
    """
    Shows some indications about the current cobol editor options:
        - free-format
        - standard (if the file is in a project config)
    """
    def activate(self):
        manager = api.plugins.get_plugin_instance(CobProjectManager)
        self.project_mode = manager is not None
        if not self.project_mode:
            manager = api.plugins.get_plugin_instance(CobFileManager)
        self.cb_standard = QtWidgets.QComboBox()
        self.cb_standard.addItems([
            'default',
            'cobol2002',
            'cobol85',
            'ibm',
            'mvs',
            'bs2000',
            'mf',
            'acu',
            'cobol2014',
            'none'
        ])
        self.cb_standard.setEditable(False)
        self.cb_standard.currentIndexChanged.connect(self._on_standard_changed)
        self.cb_free_format = QtWidgets.QCheckBox('Free format')
        self.cb_free_format.setChecked(False)
        self.cb_free_format.toggled.connect(self._on_free_format_changed)
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0,)
        layout.addWidget(self.cb_standard)
        layout.addWidget(self.cb_free_format)
        self.widget.setLayout(layout)
        api.window.add_statusbar_widget(self.widget)

        api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED,
                                 self.update)
        api.signals.connect_slot(api.signals.EDITOR_DETACHED,
                                 self.update_detached_editor)
        manager.configuration_changed.connect(self.update)
        self.update()

    @staticmethod
    def update_detached_editor(old, new):
        if isinstance(old, CobolEditor) and isinstance(new, CobolEditor):
            new.free_format = old.free_format

    def update(self, editor=None):
        if editor is None:
            editor = api.editor.get_current_editor()
        if editor is None:
            self.cb_free_format.hide()
            self.cb_standard.hide()
            return
        if isinstance(editor, CobolEditor):
            self._updating = True
            if self.project_mode:
                cfg, project = find_file_config(editor.file.path)
                if cfg is None:
                    self.cb_standard.hide()
                    self.cb_free_format.hide()
                else:
                    self.cb_standard.show()
                    self.cb_free_format.show()
                    self.cb_free_format.setChecked(cfg['free-format'])
                    editor.free_format = cfg['free-format']
                    self.cb_standard.setCurrentText(cfg['standard'])
                self.file_cfg = cfg
                self.file_project = project
            else:
                # single file mode
                self.file_cfg = get_file_config(editor.file.path)
                self.cb_standard.show()
                self.cb_standard.setCurrentText(self.file_cfg['standard'])
                self.cb_free_format.show()
                self.cb_free_format.setChecked(self.file_cfg['free-format'])
            editor.free_format = self.cb_free_format.isChecked()
            self._updating = False

    def _on_standard_changed(self, *args):
        if self._updating:
            return
        standard = self.cb_standard.currentText()
        if self.project_mode and self.file_cfg and self.file_project:
                prj_config = get_project_config(self.file_project)
                prj_config.remove(self.file_cfg)
                self.file_cfg['standard'] = standard
                prj_config.append(self.file_cfg)
                set_project_config(self.file_project, prj_config)
        elif self.file_cfg:
            self.file_cfg['standard'] = standard
            set_file_config(api.editor.get_current_path(), self.file_cfg)

    def _on_free_format_changed(self, free_format):
        if self._updating:
            return
        if self.project_mode and self.file_cfg and self.file_project:
                prj_config = get_project_config(self.file_project)
                prj_config.remove(self.file_cfg)
                self.file_cfg['free-format'] = free_format
                prj_config.append(self.file_cfg)
                set_project_config(self.file_project, prj_config)
        elif self.file_cfg:
            self.file_cfg['free-format'] = free_format
            set_file_config(api.editor.get_current_path(), self.file_cfg)
        api.editor.get_current_editor().free_format = free_format
