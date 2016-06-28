"""
This module contains the compiler settings preference page plugin.

The compiler preferences page allow the user to locate the COBOL compiler
and define the default options that will be applied foreach new target
configuration. Each target configuration will be able to change those default
settings.
"""
import os
import shlex

from PyQt5 import QtCore, QtGui, QtWidgets
from hackedit import api
from pyqode.core.api.utils import memoized

from hackedit_cobol.forms import (dlg_monospace_output_ui,
                                  settings_page_compiler_ui)
from hackedit_cobol.lib.compiler import (
    DEFAULT_CONFIG_NAME, get_default_config, set_default_config,
    get_compiler_configs, set_configs, GnuCOBOLCompiler)
from hackedit_cobol.lib.dlg_check_compiler import DlgCheckCompiler
from hackedit_cobol.lib.utils import (
    get_compilable_extensions, set_compilable_extensions,
    DEFAULT_COMPILABLE_EXTENSIONS)


_ = api.gettext.get_translation(package='hackedit-cobol')


#:  Blank config, used when adding a new config
BLANK_CONFIG = {
    'name': '',
    'cobc': '',
    'cobcrun': '',
    'environment': {
        'COB_CONFIG_DIR': '',
        'COB_COPY_DIR': '',
        'COB_LIB_PATH': ''
    },
    'output-directory': 'build',
    'standard': 'default',
    'free-format': False,
    '-static': False,
    '-debug': True,
    '-g': False,
    '-ftrace': False,
    '-ftraceall': False,
    '-fdebugging-line': False,
    'copybook-paths': [],
    'library-paths': [],
    'libraries': [],
    'extra-compiler-flags': [],
    'vcvarsall': '',
    'vcvarsall-arch': 'x86',
    'module-extension': '.dll' if api.system.WINDOWS else '.so'
                        if api.system.LINUX else '.dylib',
    'executable-extension': '.exe' if api.system.WINDOWS else ''
}


class CompilerPreferencesPlugin(api.plugins.PreferencePagePlugin):
    """
    Provides a preference page for editing the compiler configurations.
    """
    @staticmethod
    def get_preferences_page():
        """
        Returns the preference page widget.
        """
        return CompilerPreferences()


class CompilerPreferences(api.widgets.PreferencePage):
    """
    Implements the preference page where the user can define the compiler
    configurations.
    """
    def __init__(self):
        icon = QtGui.QIcon(':/icons/cobol-mimetype.png')
        super().__init__('COBOL', icon=icon)
        self.ui = settings_page_compiler_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.bt_vcvars.setVisible(api.system.WINDOWS)
        self.ui.edit_vcvars.setVisible(api.system.WINDOWS)
        self.ui.lbl_vcvars.setVisible(api.system.WINDOWS)
        self.ui.combo_arch.setVisible(api.system.WINDOWS)
        self.ui.combo_configs.currentIndexChanged.connect(self._load_config)
        self.ui.bt_copy_cfg.clicked.connect(self._copy_current_cfg)
        self.ui.bt_add_cfg.clicked.connect(self._add_cfg)
        self.ui.bt_rm_cfg.clicked.connect(self._remove_cfg)
        self.ui.bt_rename_cfg.clicked.connect(self._rename_cfg)
        self._current_index = -1
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.bt_abs_copy_path.clicked.connect(self._add_abs_copy_path)
        self.ui.bt_rel_copy_path.clicked.connect(self._add_rel_copy_path)
        self.ui.bt_rm_copy_path.clicked.connect(self._rm_copybook_path)
        self.ui.bt_abs_lib_path.clicked.connect(self._add_abs_lib_path)
        self.ui.bt_rel_lib_path.clicked.connect(self._add_rel_lib_path)
        self.ui.bt_delete_lib_path.clicked.connect(self._rm_library_path)
        self.ui.bt_choose_compiler_path.clicked.connect(
            self._select_compiler_path)
        self.ui.bt_choose_cobcrun_path.clicked.connect(
            self._select_cobcrun_path)
        self.ui.bt_check_compiler.clicked.connect(self._check_compiler)
        self.ui.bt_compiler_info.clicked.connect(self._get_compiler_info)
        self.ui.bt_runner_info.clicked.connect(self._get_runner_info)
        self.ui.bt_add_env_var.clicked.connect(self._add_env_var)
        self.ui.bt_rm_env_var.clicked.connect(self._rm_env_var)
        self.ui.bt_vcvars.clicked.connect(self._choose_vcvarsall)

    def reset(self):
        """
        Resets all fields to the values stored in the app settings.
        """
        self.ui.combo_configs.clear()
        current_index = 0
        default = get_default_config()
        for config in get_compiler_configs():
            index = self.ui.combo_configs.count()
            if config and config['name'] == default:
                current_index = index
            self.ui.combo_configs.addItem(config['name'], config)
            self.ui.combo_configs.setItemIcon(
                index, api.special_icons.run_build())
        self.ui.combo_configs.setCurrentIndex(current_index)
        self._load_config(current_index)
        self.ui.edit_extensions.setText(';'.join(
            get_compilable_extensions(
                include_preparsers=False, include_upper=False)))

    @staticmethod
    def restore_defaults():
        """
        Restore defaults settings: remove all user defined configurations.
        """
        set_configs([])
        set_default_config(DEFAULT_CONFIG_NAME)
        set_compilable_extensions(DEFAULT_COMPILABLE_EXTENSIONS)

    def save(self):
        """
        Saves the changes made to the configurations to the app's settings
        """
        if self._current_index != -1:
            self._save_current_config()
        configs = []
        for i in range(self.ui.combo_configs.count()):
            cfg = self.ui.combo_configs.itemData(i)
            if cfg['name'] != DEFAULT_CONFIG_NAME:
                configs.append(cfg)
        set_configs(configs)
        set_default_config(self.ui.combo_configs.currentText())
        set_compilable_extensions(
            [t.lower() for t in
             self.ui.edit_extensions.text().split(';') if t])

    def _save_current_config(self):
        """
        Saves changes made to the current config.

        Note the changes are not save to settings here, only in the combo box
        item's data.
        """
        cfg = self.ui.combo_configs.itemData(self._current_index)
        if cfg is None:
            return
        cfg['cobc'] = self.ui.edit_compiler_path.text()
        cfg['cobcrun'] = self.ui.edit_cobcrun_path.text()
        cfg['environment'] = {}
        for i in range(self.ui.table_env_vars.rowCount()):
            k = self.ui.table_env_vars.item(i, 0).text()
            v = self.ui.table_env_vars.item(i, 1).text()
            cfg['environment'][k] = v
        cfg['vcvarsall'] = self.ui.edit_vcvars.text()
        cfg['vcvarsall-arch'] = self.ui.combo_arch.currentText()
        cfg['output-directory'] = self.ui.edit_output_dir.text()
        cfg['-debug'] = self.ui.cb_debug.isChecked()
        cfg['-static'] = self.ui.cb_static.isChecked()
        cfg['-g'] = self.ui.cb_g.isChecked()
        cfg['-ftrace'] = self.ui.cb_ftrace.isChecked()
        cfg['-ftraceall'] = self.ui.cb_ftraceall.isChecked()
        cfg['-fdebugging-line'] = self.ui.cb_debugging_line.isChecked()
        tokens = shlex.split(self.ui.edit_extra_flags.text(), posix=False)
        cfg['extra-compiler-flags'] = [t for t in tokens if t]
        copybooks = []
        for i in range(self.ui.list_copy_paths.count()):
            copybooks.append(self.ui.list_copy_paths.item(i).text())
        cfg['copybook-paths'] = copybooks
        libs = []
        for i in range(self.ui.list_lib_paths.count()):
            libs.append(self.ui.list_lib_paths.item(i).text())
        cfg['library-paths'] = libs
        tokens = shlex.split(self.ui.edit_libs.text(), posix=False)
        cfg['libraries'] = [t for t in tokens if t]
        cfg['standard'] = self.ui.combo_standard.currentText()
        cfg['executable-extension'] = self.ui.edit_exe_ext.text()
        cfg['module-extension'] = self.ui.edit_module_ext.text()
        self.ui.combo_configs.setItemData(self._current_index, cfg)

    def _load_config(self, index):
        # remember changes to cfg (won't be applied before ``save`` is
        # called...)
        cfg = self.ui.combo_configs.itemData(index)
        default = cfg is not None and cfg['name'] == DEFAULT_CONFIG_NAME
        if self._current_index != -1:
            self._save_current_config()
        self._current_index = index
        self.ui.bt_rm_cfg.setEnabled(not default)
        self.ui.bt_rename_cfg.setEnabled(not default)
        self.ui.tab_setup.setEnabled(not default)
        self.ui.tab_options.setEnabled(not default)
        if cfg is not None:
            self.ui.edit_compiler_path.setText(cfg.get('cobc', ''))
            self.ui.edit_cobcrun_path.setText(cfg.get('cobcrun', ''))
            self.ui.table_env_vars.clearContents()
            self.ui.table_env_vars.setRowCount(0)
            for key, val in sorted(cfg['environment'].items(),
                                   key=lambda x: x[0]):
                row = self.ui.table_env_vars.rowCount()
                self.ui.table_env_vars.insertRow(row)
                self.ui.table_env_vars.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(key))
                self.ui.table_env_vars.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(val))
            self.ui.edit_vcvars.setText(cfg['vcvarsall'])
            self.ui.combo_arch.setCurrentIndex(
                0 if cfg['vcvarsall-arch'] == 'x86' else 1)
            self.ui.edit_output_dir.setText(cfg['output-directory'])
            self.ui.cb_debug.setChecked(cfg['-debug'])
            self.ui.cb_static.setChecked(cfg['-static'])
            self.ui.cb_g.setChecked(cfg['-g'])
            self.ui.cb_ftrace.setChecked(cfg['-ftrace'])
            self.ui.cb_ftraceall.setChecked(cfg['-ftraceall'])
            self.ui.cb_debugging_line.setChecked(cfg['-fdebugging-line'])
            self.ui.edit_extra_flags.setText(
                ' '.join(cfg['extra-compiler-flags']))
            self.ui.list_copy_paths.clear()
            for path in cfg['copybook-paths']:
                self.ui.list_copy_paths.addItem(path)
            self.ui.list_lib_paths.clear()
            for path in cfg['library-paths']:
                self.ui.list_lib_paths.addItem(path)
            self.ui.edit_libs.setText(' '.join(cfg['libraries']))
            self.ui.label_read_only.setHidden(not default)
            self.ui.combo_standard.setCurrentText(cfg['standard'])
            self.ui.edit_exe_ext.setText(cfg['executable-extension'])
            self.ui.edit_module_ext.setText(cfg['module-extension'])
            if default:
                self.ui.bt_copy_cfg.setFocus()
            else:
                self.ui.bt_check_compiler.setFocus()
            version = GnuCOBOLCompiler.get_version(cfg, include_all=False)
            if version == 'Compiler not found':
                self.ui.lbl_cobc_version.hide()
            else:
                self.ui.lbl_cobc_version.show()
                self.ui.lbl_cobc_version.setText('cobc v%s' % version)
        else:
            self.ui.edit_compiler_path.setText('')
            self.ui.table_env_vars.clearContents()
            self.ui.table_env_vars.setRowCount(0)
            self.ui.edit_vcvars.setText('')
            self.ui.combo_arch.setCurrentIndex(0)
            self.ui.edit_output_dir.setText('')
            self.ui.cb_debug.setChecked(False)
            self.ui.cb_static.setChecked(False)
            self.ui.cb_g.setChecked(False)
            self.ui.cb_ftrace.setChecked(False)
            self.ui.cb_ftraceall.setChecked(False)
            self.ui.cb_debugging_line.setChecked(False)
            self.ui.edit_extra_flags.setText('')
            self.ui.list_copy_paths.clear()
            self.ui.list_lib_paths.clear()
            self.ui.edit_libs.setText('')
            self.ui.lbl_cobc_version.setText('')

    def _get_config_names(self):
        return [self.ui.combo_configs.itemText(i) for i in range(
            self.ui.combo_configs.count())]

    def _get_safe_name(self, title='New compiler configuration',
                       default='', ignore=None):
        if ignore is None:
            ignore = []
        ok = False
        names = self._get_config_names()
        while not ok:
            name, status = QtWidgets.QInputDialog.getText(
                self, title,
                _('Please enter a unique name for the configuration:'),
                QtWidgets.QLineEdit.Normal, default)
            if not status:
                return None
            ok = name not in names or name in ignore
            if not ok:
                QtWidgets.QMessageBox.warning(
                    self, _('Invalid name'),
                    _('The name %r is already used for another configuration. '
                      'Please choose another name...') % name)
        return name

    def _add_cfg(self):
        name = self._get_safe_name()
        if name:
            ncfg = BLANK_CONFIG.copy()
            ncfg['name'] = name
            ncfg['output-directory'] = 'build-%s' % name.replace(' ', '-')
            index = self.ui.combo_configs.count()
            self.ui.combo_configs.addItem(name, ncfg)
            self.ui.combo_configs.setItemIcon(
                index, api.special_icons.run_build())
            self.ui.combo_configs.setCurrentIndex(index)

    def _remove_cfg(self):
        answer = QtWidgets.QMessageBox.question(
            self, _('Remove compiler configuration'),
            _('Are you sure you want to remove the configuration %r?') %
            self.ui.combo_configs.currentText())
        if answer == QtWidgets.QMessageBox.Yes:
            self.ui.combo_configs.removeItem(
                self.ui.combo_configs.currentIndex())

    def _rename_cfg(self):
        cfg = self.ui.combo_configs.currentData()
        old_name = cfg['name']
        name = self._get_safe_name(title='Rename configuration',
                                   default=old_name, ignore=[old_name])
        if name and name != old_name:
            cfg['name'] = name
            index = self.ui.combo_configs.currentIndex()
            self.ui.combo_configs.setItemData(index, cfg)
            self.ui.combo_configs.setItemText(index, name)

    def _copy_current_cfg(self):
        cfg = self.ui.combo_configs.currentData()
        name = self._get_safe_name(title='Copy configuration',
                                   default='Copy of %s' % cfg['name'])
        if name:
            assert isinstance(cfg, dict)
            ncfg = cfg.copy()
            ncfg['name'] = name
            ncfg['output-directory'] = 'build-%s' % name.replace(' ', '-')
            index = self.ui.combo_configs.count()
            self.ui.combo_configs.addItem(name, ncfg)
            self.ui.combo_configs.setItemIcon(
                index, api.special_icons.run_build())
            self.ui.combo_configs.setCurrentIndex(index)

    def _add_abs_copy_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, _('Select a copybook path'), os.path.expanduser('~'))
        if path:
            self.ui.list_copy_paths.addItem(os.path.normpath(path))

    def _add_rel_copy_path(self):
        path, status = QtWidgets.QInputDialog.getText(
            self, _('Add relative copybook path'), 'Path:')
        if status:
            self.ui.list_copy_paths.addItem(path)

    def _rm_copybook_path(self):
        current = self.ui.list_copy_paths.currentRow()
        if current != -1:
            self.ui.list_copy_paths.takeItem(current)

    def _add_abs_lib_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, _('Select a library path'), os.path.expanduser('~'))
        if path:
            self.ui.list_lib_paths.addItem(os.path.normpath(path))

    def _add_rel_lib_path(self):
        path, status = QtWidgets.QInputDialog.getText(
            self, _('Add relative library path'), 'Path:')
        if status:
            self.ui.list_lib_paths.addItem(path)

    def _rm_library_path(self):
        current = self.ui.list_lib_paths.currentRow()
        if current != -1:
            self.ui.list_lib_paths.takeItem(current)

    def _select_compiler_path(self):
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Select path to a GnuCOBOL compiler executable (cobc).'),
            self.ui.edit_compiler_path.text())
        if path:
            self.ui.edit_compiler_path.setText(os.path.normpath(path))

    def _select_cobcrun_path(self):
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self,
            _('Select path to a GnuCOBOL module runner executable (cobcrun)'),
            self.ui.edit_cobcrun_path.text())
        if path:
            self.ui.edit_cobcrun_path.setText(os.path.normpath(path))

    def _check_compiler(self):
        self._save_current_config()
        cfg = self.ui.combo_configs.itemData(self._current_index)
        DlgCheckCompiler.check(self, cfg)

    def _get_compiler_info(self):
        from hackedit_cobol.lib.compiler import GnuCOBOLCompiler
        cfg = self.ui.combo_configs.itemData(self._current_index)
        info = GnuCOBOLCompiler(cfg).get_cobc_info()
        DlgInfo.show_information(
            self, _('Compiler information'), info)

    def _get_runner_info(self):
        from hackedit_cobol.lib.compiler import GnuCOBOLCompiler
        cfg = self.ui.combo_configs.itemData(self._current_index)
        info = GnuCOBOLCompiler(cfg).get_cobcrun_runtime_env()
        DlgInfo.show_information(
            self, _('Module runner runtime environment'), info)

    def _add_env_var(self):
        index = self.ui.table_env_vars.rowCount()
        self.ui.table_env_vars.insertRow(index)
        focus_item = QtWidgets.QTableWidgetItem()
        self.ui.table_env_vars.setItem(index, 0, focus_item)
        self.ui.table_env_vars.setItem(index, 1, QtWidgets.QTableWidgetItem())
        self.ui.table_env_vars.scrollToItem(focus_item)
        self.ui.table_env_vars.editItem(focus_item)

    def _rm_env_var(self):
        self.ui.table_env_vars.removeRow(self.ui.table_env_vars.currentRow())

    def _choose_vcvarsall(self):
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select vcvarsall.bat", 'C:\\Program Files (x86)',
            _('Batch files (*.bat)'))
        if path:
            self.ui.edit_vcvars.setText(path)


class DlgInfo(QtWidgets.QDialog):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.ui = dlg_monospace_output_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.setFont(QtGui.QFont(
            QtCore.QSettings().value('editor/font', 'Hack'),
            int(QtCore.QSettings().value('editor/font_size'))))
        self.ui.textEdit.setPlainText(text)
        self.ui.textEdit.adjustSize()

    @staticmethod
    def show_information(parent, title, information):
        DlgInfo(parent, title, information).exec_()


@memoized
def get_cobc_infos_memoized(cfg_repr):
    cfg = eval(cfg_repr)
    from hackedit_cobol.lib.compiler import GnuCOBOLCompiler
    return GnuCOBOLCompiler(cfg).get_cobc_info()
