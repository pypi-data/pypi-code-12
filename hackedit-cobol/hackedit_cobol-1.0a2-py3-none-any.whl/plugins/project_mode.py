"""
This module contains the COBOL project manager plugin.
"""
import json
import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from hackedit import api

from hackedit_cobol.lib.build_thread import BuildThreadBase
from hackedit_cobol.lib.compiler import GnuCOBOLCompiler, MODULE, \
    DEFAULT_CONFIG_NAME, get_compiler_config
from hackedit_cobol.lib.dlg_configure import DlgConfigureBase
from hackedit_cobol.lib.events import FileNotInProjectEvent
from hackedit_cobol.lib.manager_plugin_base import CobolManagerPluginBase
from hackedit_cobol.lib.preparsers import get_preparser_for_file
from hackedit_cobol.lib.utils import get_compilable_filter, is_compilable


_ = api.gettext.get_translation(package='hackedit-cobol')


class CobProjectManager(CobolManagerPluginBase):
    """
    COBOL project manager: let you define how to build and run your COBOL
    projects.
    """
    def activate(self):
        """
        Initializes the plugin.
        """
        self._flg_not_in_projects = []
        self._flg_run = False
        self.build_thread = None
        self.setup_ui()
        self.load_run_configs()
        self.connect_slots()
        api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED,
                                 self._on_editor_changed)
        self.configuration_changed.connect(self._on_config_changed)

    def setup_ui(self):
        super().setup_ui()
        # run configurations
        cob_menu = api.window.get_menu('C&OBOL')
        cob_toolbar = api.window.get_toolbar('cobolToolBar', 'COBOLToolBar')
        self.mnu_run_configs = cob_menu.addMenu(_('Run configurations'))
        self.combo_run_configs = QtWidgets.QComboBox()
        self.combo_run_configs.setToolTip(_('The list of run targets'))
        cob_toolbar.insertWidget(self.a_run, self.combo_run_configs)

    def apply_preferences(self):
        self._on_config_changed()
        self.a_configure.setShortcut(api.shortcuts.get(
            'Configure', _('Configure'), 'F8'))
        self.a_build.setShortcut(api.shortcuts.get(
            'Build', _('Build'), 'Ctrl+B'))
        self.a_clean.setShortcut(api.shortcuts.get(
            'Clean', _('Clean'), 'Ctrl+Alt+C'))
        self.a_rebuild.setShortcut(
            api.shortcuts.get('Rebuild', _('Rebuild'), 'Ctrl+Alt+B'))
        self.a_run.setShortcut(api.shortcuts.get(
            'Run', _('Run'), 'F9'))

    def _on_config_changed(self):
        self.load_run_configs()
        self.enable_build_actions()
        for editor in api.editor.get_all_editors():
            try:
                linter = editor.modes.get('CobolLinterMode')
            except KeyError:
                _logger().debug('editor %r has no CobolLinterMode', editor)
            else:
                linter.request_analysis()

    def connect_slots(self):
        # run configs slots
        api.signals.connect_slot(api.signals.CURRENT_PROJECT_CHANGED,
                                 self.load_run_configs)
        self.combo_run_configs.currentIndexChanged.connect(
            self._on_combo_run_configs_index_changed)
        # menu actions
        self.a_configure.triggered.connect(self.configure)
        self.a_clean.triggered.connect(self.clean)
        self.a_build.triggered.connect(self.build)
        self.a_run.triggered.connect(self.run)
        self.a_rebuild.triggered.connect(self.rebuild)
        self.configuration_changed.connect(self._on_config_changed)

    def load_run_configs(self):
        self.mnu_run_configs.clear()
        self.combo_run_configs.clear()
        with api.utils.block_signals(self.combo_run_configs):
            path = api.project.get_current_project()
            configs = get_project_config(path)
            current = get_current_run_config(path)
            ag = QtWidgets.QActionGroup(self.mnu_run_configs)
            for cfg in configs:
                try:
                    cfg['run']
                except KeyError:
                    _logger().debug('no run settings in config: %r', cfg)
                else:
                    name = QtCore.QFileInfo(cfg['path']).completeBaseName()
                    icon = QtGui.QIcon.fromTheme('application-x-executable')
                    self.combo_run_configs.addItem(icon, name, cfg)
                    action = self.mnu_run_configs.addAction(name)
                    assert isinstance(action, QtWidgets.QAction)
                    action.setIcon(icon)
                    action.setCheckable(True)
                    action.setData(cfg)
                    if name == current:
                        action.setChecked(True)
                    ag.addAction(action)
            for i in range(self.combo_run_configs.count()):
                text = self.combo_run_configs.itemText(i)
                if text == current:
                    self.combo_run_configs.setCurrentIndex(i)
                    break
            self.combo_run_configs.adjustSize()
        ag.triggered.connect(self._on_action_run_cfg_triggered)

    def configure(self):
        prj = api.project.get_current_project()
        ret_val = DlgConfigureProject.configure(prj, self.main_window)
        if ret_val:
            self.configuration_changed.emit()
            return True
        return False

    @staticmethod
    def get_preparser_cobol_output(cfg):
        project_path = api.project.get_current_project()
        abs_path = os.path.abspath(
            os.path.join(project_path, cfg['path']))
        preparser = get_preparser_for_file(abs_path)
        if preparser and not preparser.only_preparser:
            return preparser.get_output_file_path(abs_path)
        return ''

    def clean(self):
        project_path = api.project.get_current_project()
        prj_cfg = get_project_config(project_path)
        removed_paths = []

        for cfg in prj_cfg:
            path = self.get_preparser_cobol_output(cfg)
            if self._remove_path(path):
                removed_paths.append(path)

        for cfg_name in [get_project_compiler(project_path)] + \
                get_secondary_compilers(project_path):
            cfg = get_compiler_config(cfg_name)
            if not cfg:
                continue
            path = os.path.join(project_path, cfg['output-directory'])
            if self._remove_path(path):
                removed_paths.append(path)

        ev = api.events.Event(
            _('Clean finished'),
            _('The following files were removed:\n  -%s') % '\n  -'.join(
                removed_paths) if removed_paths else
            _('There were no file to remove...'))
        api.events.post(ev, force_show=True,
                        show_balloon=not self.main_window.isVisible())
        self.enable_build_actions()

    def build(self):
        if self.build_thread:
            self.build_thread.abort = True
        else:
            api.editor.save_all_editors()
            self.a_build.setIcon(QtGui.QIcon.fromTheme('process-stop'))
            self.a_build.setText(_('Cancel build'))
            self.a_build.setToolTip(_('Cancel build'))
            self.a_configure.setEnabled(False)
            self.a_clean.setEnabled(False)
            self.a_rebuild.setEnabled(False)
            self.mnu_run_configs.setEnabled(False)
            self.combo_run_configs.setEnabled(False)
            self.a_run.setEnabled(False)
            if self.build_output:
                self.build_output.clear()
            if self.issues_table:
                self.issues_table.clearContents()
                self.issues_table.setRowCount(0)
            self.build_thread = BuildThread(api.project.get_current_project())
            self.build_thread.command_finished.connect(
                self._on_command_finished)
            self.build_thread.errored.connect(self._on_build_errored)
            self.build_thread.finished.connect(self._on_build_finished)
            self.build_thread.configuration_message.connect(
                self._on_config_message)
            self.build_thread.configuration_skipped.connect(
                self._on_config_skipped)
            self.build_thread.start()

    def _on_build_finished(self, success):
        super()._on_build_finished(success)
        self.a_configure.setEnabled(True)
        self.mnu_run_configs.setEnabled(True)
        self.combo_run_configs.setEnabled(True)

    @staticmethod
    def get_executable_path(cfg):
        project_path = api.project.get_current_project()
        original_config = get_compiler_config(
            get_project_compiler(project_path))
        abs_path = os.path.abspath(
            os.path.join(project_path, cfg['path']))
        preparser = get_preparser_for_file(abs_path)
        if preparser and preparser.only_preparser:
            return preparser.get_output_file_path(abs_path)
        else:
            compiler = GnuCOBOLCompiler(BuildThread.setup_overrides(
                original_config.copy(), cfg))
            executable = cfg['filetype'] != MODULE
            return compiler.get_output_path(abs_path, executable=executable)

    def _run(self):
        self._flg_run = False
        cfg = self.combo_run_configs.currentData()
        path = self.get_executable_path(cfg)
        if cfg['run']['external-terminal']:
            self._run_in_external_terminal(cfg, path)
        else:
            self._run_embedded(cfg, path)

    def _run_in_external_terminal(self, cfg, path):
        prj_path = api.project.get_current_project()
        cfg_name = get_project_compiler(prj_path)
        self.run_in_external_terminal(path, cfg, cfg_name)

    def _run_embedded(self, cfg, path):
        if self.run_dock is None:
            self._setup_run_dock()
        prj_path = api.project.get_current_project()
        compiler_cfg_name = get_project_compiler(prj_path)
        compiler_cfg = get_compiler_config(compiler_cfg_name)
        self.run_dock.show()
        if cfg['filetype'] == MODULE:
            pgm = compiler_cfg['cobcrun']
            args = [QtCore.QFileInfo(path).completeBaseName()] + \
                cfg['run']['arguments']
        else:
            pgm = path
            args = cfg['run']['arguments']

        self.run_embedded(pgm, args, cfg, compiler_cfg, path)

    def check_compiler(self):
        prj = api.project.get_current_project()
        cfg = get_compiler_config(get_project_compiler(prj))
        if cfg is None:
            set_project_compiler(prj, 'Default')
            cfg = get_compiler_config(get_project_compiler(prj))
        self._compiler_works = GnuCOBOLCompiler.is_working(cfg)
        return self._compiler_works

    def enable_build_actions(self):
        enable_build_actions = len(get_project_config(
            api.project.get_current_project())) > 0
        self.a_build.setEnabled(enable_build_actions)
        self.a_clean.setEnabled(enable_build_actions)
        self.a_run.setEnabled(enable_build_actions)
        self.a_rebuild.setEnabled(enable_build_actions)
        self.a_configure.setEnabled(True)

    def _on_action_run_cfg_triggered(self, action):
        name = action.text().replace('&', '')
        set_current_run_config(api.project.get_current_project(), name)
        index = self.combo_run_configs.findText(name)
        with api.utils.block_signals(self.combo_run_configs):
            self.combo_run_configs.setCurrentIndex(index)
        self.check_compiler()
        self.enable_build_actions()

    def _on_combo_run_configs_index_changed(self, index):
        name = self.combo_run_configs.itemText(index)
        if name:
            set_current_run_config(api.project.get_current_project(), name)
        for action in self.mnu_run_configs.actions():
            if action.text().replace('&', '') == name:
                action.setChecked(True)
                break
        self.enable_build_actions()

    def _on_editor_changed(self, editor):
        from hackedit_cobol.plugins.editor import CobolEditor
        # check if file is in project config, if not show a notification
        # to warn the user and provide a quick way to add it to the project
        # config
        if isinstance(editor, CobolEditor):
            path = editor.file.path
            cfg, project = find_file_config(path)
            if cfg is None and project is not None and \
                    path not in self._flg_not_in_projects and \
                    is_compilable(path):
                api.events.post(FileNotInProjectEvent(path, project, self),
                                force_show=True)
                self._flg_not_in_projects.append(path)


class BuildThread(BuildThreadBase):
    def __init__(self, project_path):
        self.project_path = project_path
        self.abort = False
        super().__init__()

    def build(self):
        compiler_cfg = get_compiler_config(
            get_project_compiler(self.project_path))

        compiler_names = [get_project_compiler(self.project_path)] + \
            get_secondary_compilers(self.project_path)

        prj_cfg = get_project_config(self.project_path)
        build_directories = []
        success = True
        prefix = ''

        for compiler_name in compiler_names:
            compiler_cfg = get_compiler_config(compiler_name)

            if compiler_cfg is None:
                continue

            self.configuration_message.emit(
                prefix + 'Compiler configuration: %r' % compiler_name)
            prefix = '\n'

            output = compiler_cfg['output-directory']
            if output in build_directories:
                self.configuration_skipped.emit(
                    'Compiler configuration %r skipped because the output '
                    'directory has already been used by a previous '
                    'configuration...' % compiler_name)
                continue

            build_directories.append(output)

            for fcfg in prj_cfg:
                # user cancled build
                if self.abort is True:
                    success = False
                    break

                abs_path = os.path.abspath(
                    os.path.join(self.project_path, fcfg['path']))

                # preparse
                preparser = get_preparser_for_file(abs_path)
                if preparser:
                    success = self.preparse(fcfg, preparser, abs_path)
                    if not success or preparser.only_preparser:
                        continue
                    else:
                        # change config to use the preparser output and
                        # continue normal build procedure.
                        fcfg = fcfg.copy()
                        abs_path = preparser.get_output_file_path(abs_path)
                        fcfg['path'] = os.path.split(abs_path)[1]

                # compile
                compiler = GnuCOBOLCompiler(self.setup_overrides(
                    compiler_cfg.copy(), fcfg, preparser))
                success = self.compile(fcfg, compiler, abs_path,
                                       self.project_path)

        self.finished.emit(success)


class DlgConfigureProject(DlgConfigureBase):
    """
    Dialog that let user configure how to build and run the current editor.
    """
    def get_configs(self):
        if self._current_index != -1:
            self._update_current_data()
        lw = self.ui.list_build
        configs = [lw.item(i).data(QtCore.Qt.UserRole)
                   for i in range(lw.count())]
        return configs

    def __init__(self, project_path, parent):
        super().__init__(parent, title='Configure project')
        self._update_flg = False
        self.project_path = project_path
        compiler = get_project_compiler(project_path)
        self.ui.combo_compilers.setCurrentText(compiler)
        self.ui.list_build.currentRowChanged.connect(self._on_file_changed)
        self.ui.cb_compile_submodules.hide()
        self.ui.cb_compile_submodules.setEnabled(False)
        self._current_index = -1
        self._on_file_changed(-1)
        current = get_current_run_config(project_path)
        file_configs = get_project_config(project_path)
        row = 0
        for i, file_cfg in enumerate(file_configs):
            item = QtWidgets.QListWidgetItem()
            path = file_cfg['path']
            item.setText(path)
            item.setIcon(QtGui.QIcon(':/icons/cobol-mimetype-big.png'))
            if QtCore.QFileInfo(path).baseName() == current:
                row = i
            item.setData(QtCore.Qt.UserRole, file_cfg)
            self.ui.list_build.addItem(item)
        if file_configs:
            self.ui.list_build.setCurrentRow(row)
        self.ui.bt_add_build.clicked.connect(self._add_file)
        self.ui.bt_remove_build.clicked.connect(self._rm_file)
        self.ui.combo_compilers.currentIndexChanged.connect(
            self._update_current_config_display)
        self.ui.group_override_build_options.toggled.connect(
            self._udpate_overrides)
        self.ui.bt_move_build_down.clicked.connect(self._move_down)
        self.ui.bt_move_build_up.clicked.connect(self._move_up)

        self.ui.tabWidget.setTabIcon(0, api.special_icons.run_build())
        self.ui.tabWidget.setTabIcon(1, api.special_icons.run_icon())
        self.secondary_compilers = get_secondary_compilers(project_path)

    def _move_down(self):
        r = self.ui.list_build.currentRow()
        item = self.ui.list_build.takeItem(r)
        n = r + 1
        self.ui.list_build.insertItem(n, item)
        self.ui.list_build.setCurrentRow(n)

    def _move_up(self):
        r = self.ui.list_build.currentRow()
        item = self.ui.list_build.takeItem(r)
        n = r - 1
        self.ui.list_build.insertItem(n, item)
        self.ui.list_build.setCurrentRow(n)

    def _update_current_config_display(self, _):
        if self._update_flg is False:
            self._update_flg = True
            current_file_item = self.ui.list_build.currentItem()
            data = None
            if current_file_item:
                data = current_file_item.data(QtCore.Qt.UserRole)
            self._display_config(data)
            self._update_flg = False

    def _rm_file(self):
        cfg = self.ui.list_build.currentItem().data(QtCore.Qt.UserRole)
        a = QtWidgets.QMessageBox.question(
            self, _('Remove file from build'),
            _('Are you sure you want to remove %r from the project build '
              'configuration?') % cfg['path'])
        if a == QtWidgets.QMessageBox.Yes:
            self.ui.list_build.takeItem(self.ui.list_build.currentRow())

    def _add_file(self):
        # todo add filter for only cobol files.
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Add file to build'), self.project_path,
            get_compilable_filter() + _(';; All files (*.*)'))
        if path and os.path.exists(path):
            rel_path = os.path.relpath(path, self.project_path)
            if rel_path.startswith('..'):
                answer = QtWidgets.QMessageBox.question(
                    self, _('File outside of project root!'),
                    _('The file is outside of the project root! This might '
                      'cause some issues if you put the project configuration '
                      'under versioning and open it on another environemnt.\n'
                      'Are you sure you want to add that file?'))
                if answer == QtWidgets.QMessageBox.No:
                    return
            ftype = GnuCOBOLCompiler.get_file_type(path)
            if ftype == MODULE:
                cfg = self.DEFAULT_MODULE_CFG
            else:
                cfg = self.DEFAULT_EXECUTABLE_CFG
            cfg['path'] = os.path.normpath(rel_path)
            index = self.ui.list_build.count()
            item = QtWidgets.QListWidgetItem()
            item.setText(cfg['path'])
            item.setIcon(QtGui.QIcon(':/icons/cobol-mimetype-big.png'))
            item.setData(QtCore.Qt.UserRole, cfg)
            self.ui.list_build.addItem(item)
            self.ui.list_build.setCurrentRow(index)

    def _on_file_changed(self, index):
        if self._current_index != -1:
            self._update_current_data()
        self._current_index = index
        if index != -1:
            cfg = self.ui.list_build.currentItem().data(QtCore.Qt.UserRole)
            self._display_config(cfg)
        self._update_states(index)

    def _display_config(self, cfg):
        if cfg:
            absolute_path = os.path.abspath(os.path.join(
                self.project_path, cfg['path']))
            self.display_file_config(cfg, absolute_path)
        else:
            self.display_file_config(None, None)

    def _update_current_data(self):
        """
        Update the configuration of the currently selected file.

        Read field values and store item data.
        """
        item = self.ui.list_build.item(self._current_index)
        if item is None:
            return
        path = item.data(QtCore.Qt.UserRole)['path']
        item.setData(QtCore.Qt.UserRole, self.get_current_config(path))

    def _update_states(self, index):
        self.ui.tabWidget.setEnabled(index != -1)
        self.ui.bt_remove_build.setEnabled(index != -1)
        max_index = self.ui.list_build.count() - 1
        min_index = 0
        self.ui.bt_move_build_down.setEnabled(
            index != -1 and index < max_index)
        self.ui.bt_move_build_up.setEnabled(index != -1 and index > min_index)

    @staticmethod
    def configure(project_path, parent):
        """
        Changes project configuration.

        :param project_path: path of the project to edit
        :param parent: parent widget of the dialog.

        :returns: True if dialog was accepted, False if dialog was rejected.
        """
        dlg = DlgConfigureProject(project_path, parent)
        if dlg.exec_() == dlg.Accepted:
            # save project config
            try:
                set_project_config(project_path, dlg.get_configs())
                set_project_compiler(project_path, dlg.get_compiler())
                set_secondary_compilers(project_path, dlg.secondary_compilers)
            except PermissionError as e:
                QtWidgets.QMessageBox.warning(
                    parent, _('Permission error'),
                    _('Failed to save project configuration.\n\n%s') % e)
                return False
            else:
                current_item = dlg.ui.list_build.currentItem()
                if current_item:
                    current = current_item.text()
                    set_current_run_config(
                        project_path,
                        QtCore.QFileInfo(current).completeBaseName())
                return True
        return False


def get_current_run_config(project_path):
    """
    Returns the current run configuration.
    """
    usd = api.project.load_user_config(project_path)
    try:
        name = usd['current_run_config']
    except KeyError:
        name = ''
    return name.replace('&', '')


def set_current_run_config(project_path, name):
    usd = api.project.load_user_config(project_path)
    usd['current_run_config'] = name.replace('&', '')
    api.project.save_user_config(project_path, usd)


def get_project_config_path(project_path):
    p = os.path.join(project_path, api.project.FOLDER, 'project.json')
    return p


def get_project_config(project_path):
    """
    Gets the project configuration.

    The configuration consist in a list of file build configs.
    """

    def load():
        try:
            with open(get_project_config_path(project_path)) as f:
                return json.load(f)
        except OSError:
            return []

    def sanitize(cfg):
        # remove files that do not exist anymore.
        to_remove = []
        for fcfg in cfg:
            full_path = os.path.join(project_path, fcfg['path'])
            if not os.path.exists(full_path):
                to_remove.append(fcfg)
        for rm in to_remove:
            cfg.remove(rm)
        return cfg

    return sanitize(load())


def set_project_config(project_path, config):
    """
    Saves the project configuration to ``.hackedit/project.json``
    """
    try:
        with open(get_project_config_path(project_path), 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4)
    except OSError:
        _logger().exception('failed to set project config')


def get_project_compiler(project_path):
    """
    Gets the name of project's compiler configuration.

    :param project_path: project path.
    """
    usd = api.project.load_user_config(project_path)
    try:
        return usd['compiler']
    except KeyError:
        return DEFAULT_CONFIG_NAME


def set_project_compiler(project_path, name):
    """
    Saves the project compiler to user data.

    :param project_path: project path
    """
    usd = api.project.load_user_config(project_path)
    usd['compiler'] = name
    api.project.save_user_config(project_path, usd)


def get_secondary_compilers(project_path):
    """
    Gets the list of secondary compilers to run after the main compiler.

    :param project_path: project path.
    """
    usd = api.project.load_user_config(project_path)
    try:
        compilers = usd['secondary-compilers']
    except KeyError:
        compilers = []
    return [c for c in compilers if get_compiler_config(c) is not None]


def set_secondary_compilers(project_path, secondary_compilers):
    """
    Sets the list of secondary compilers to run after the main compiler.

    :param project_path: project path.
    """
    usd = api.project.load_user_config(project_path)
    usd['secondary-compilers'] = secondary_compilers
    api.project.save_user_config(project_path, usd)


def find_file_config(path):
    """
    Finds the file config and the associated project.

    :param path: path of the file to search.
    :returns: config, project_path
    """
    associated_project = None
    for project in api.project.get_projects():
        file_path = os.path.relpath(path, project)
        if not file_path.startswith('..'):
            associated_project = project
        cfg = get_project_config(project)
        for file_cfg in cfg:
            if file_cfg['path'] == file_path:
                return file_cfg, project
    return None, associated_project


def _logger():
    return logging.getLogger(__name__)
