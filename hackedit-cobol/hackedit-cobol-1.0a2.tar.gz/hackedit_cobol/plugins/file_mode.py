"""
This module contains the CobFileManager which allow to configure, clean, build
and rebuild the current editor.
"""
import json
import logging

from PyQt5 import QtCore, QtGui
from hackedit import api

from hackedit_cobol.lib.build_thread import BuildThreadBase
from hackedit_cobol.lib.compiler import GnuCOBOLCompiler, MODULE, \
    DEFAULT_CONFIG_NAME, get_compiler_config
from hackedit_cobol.lib.dlg_configure import DlgConfigureBase
from hackedit_cobol.lib.manager_plugin_base import CobolManagerPluginBase
from hackedit_cobol.lib.preparsers import get_preparser_for_file
from hackedit_cobol.lib.utils import is_compilable, get_submodules


_ = api.gettext.get_translation(package='hackedit-cobol')


class CobFileManager(CobolManagerPluginBase):
    """
    COBOL file manager: let you define how to build and run the current COBOL
    editor.
    """
    configuration_changed = QtCore.pyqtSignal()

    def activate(self):
        """
        Initializes the plugin.
        """
        self.build_output_dock = None
        self.build_output = None
        self.issues_dock = None
        self.issues_table = None
        self.run_dock = None
        self.run_widget = None
        self._flg_run = False
        self._first_apply = True
        self.build_thread = None
        self.setup_ui()
        self.connect_slots()
        self.configuration_changed.connect(self._on_config_changed)

    def apply_preferences(self):
        self._on_config_changed()
        self.a_configure.setShortcut(api.shortcuts.get(
            'Configure', _('Configure'), 'F8'))
        self.a_build.setShortcut(api.shortcuts.get(
            'Build', _('Build'), 'Ctrl+B'))
        self.a_clean.setShortcut(api.shortcuts.get(
            'Clean', _('Clean'), 'Ctrl+Alt+C'))
        self.a_rebuild.setShortcut(api.shortcuts.get(
            'Rebuild', _('Rebuild'), 'Ctrl+Alt+B'))
        self.a_run.setShortcut(api.shortcuts.get(
            'Run', _('Run'), 'F9'))

    def _on_config_changed(self):
        self.enable_build_actions()
        for editor in api.editor.get_all_editors():
            # rerun linter with the given config.
            try:
                linter = editor.modes.get('CobolLinterMode')
            except KeyError:
                _logger().warn('no CobolLinterMode on editor %r', editor)
            else:
                linter.request_analysis()

    def connect_slots(self):
        # menu actions
        self.a_configure.triggered.connect(self.configure)
        self.a_clean.triggered.connect(self.clean)
        self.a_build.triggered.connect(self.build)
        self.a_run.triggered.connect(self.run)
        self.a_rebuild.triggered.connect(self.rebuild)
        self.configuration_changed.connect(self._on_config_changed)
        api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED,
                                 self.enable_build_actions)

    def configure(self):
        path = api.editor.get_current_path()
        ret_val = DlgConfigureFile.configure(path, self.main_window)
        if ret_val:
            self.configuration_changed.emit()
            return True
        return False

    @staticmethod
    def get_executable_path(file_cfg, compiler_cfg):
        fpath = file_cfg['path']
        preparser = get_preparser_for_file(fpath)
        if preparser and preparser.only_preparser:
            return None
        else:
            compiler = GnuCOBOLCompiler(BuildThread.setup_overrides(
                compiler_cfg, file_cfg))
            executable = file_cfg['filetype'] != MODULE
            output = compiler.get_output_path(fpath, executable=executable)
            return output

    def clean(self):
        def get_preparser_cobol_output(path):
            preparser = get_preparser_for_file(path)
            if preparser and not preparser.only_preparser:
                return preparser.get_output_file_path(path)
            return ''

        def get_all_source_files():
            fpath = api.editor.get_current_path()
            fcfg = get_file_config(fpath)
            try:
                include_submodules = fcfg['compile-submodules']
            except KeyError:
                paths = [fpath]
            else:
                if include_submodules:
                    submodules = get_submodules(fpath, recursive=True)
                    paths = [fpath] + submodules
                else:
                    paths = [fpath]
            return paths

        # get the list of all compilers config (including secondary compilers)
        fpath = api.editor.get_current_path()
        cfg = get_compiler_config(get_file_compiler(fpath))
        compiler_configs = [cfg] + [get_compiler_config(name) for name in
                                    get_secondary_compilers(fpath)]

        # get the list of source files to clean, including submodules if any
        source_files = get_all_source_files()
        removed_paths = []
        for path in source_files:
            file_cfg = get_file_config(path)
            out_path = get_preparser_cobol_output(path)
            if self._remove_path(out_path):
                removed_paths.append(out_path)
            for compiler_cfg in compiler_configs:
                out_path = self.get_executable_path(file_cfg, compiler_cfg)
                if self._remove_path(out_path):
                    removed_paths.append(out_path)

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
            self.a_run.setEnabled(False)
            if self.build_output:
                self.build_output.clear()
            if self.issues_table:
                self.issues_table.clearContents()
                self.issues_table.setRowCount(0)
            self.build_thread = BuildThread(api.editor.get_current_path())
            self.build_thread.command_finished.connect(
                self._on_command_finished)
            self.build_thread.errored.connect(self._on_build_errored)
            self.build_thread.finished.connect(self._on_build_finished)
            self.build_thread.configuration_message.connect(
                self._on_config_message)
            self.build_thread.configuration_skipped.connect(
                self._on_config_skipped)
            self.build_thread.start()

    def _run(self):
        self._flg_run = False
        fpath = api.editor.get_current_path()
        cfg = get_file_config(fpath)
        compiler_cfg = get_compiler_config(get_file_compiler(fpath))
        path = self.get_executable_path(cfg, compiler_cfg)
        if cfg['run']['external-terminal']:
            self._run_in_external_terminal(cfg, path)
        else:
            self._run_embedded(cfg, path)

    def _run_in_external_terminal(self, cfg, path):
        cfg_name = get_file_compiler(api.editor.get_current_path())
        self.run_in_external_terminal(path, cfg, cfg_name)

    def _run_embedded(self, cfg, path):
        if self.run_dock is None:
            self._setup_run_dock()
        self.run_dock.show()

        cfg_name = get_file_compiler(api.editor.get_current_path())
        compiler_cfg = get_compiler_config(cfg_name)
        if cfg['filetype'] == MODULE:
            pgm = compiler_cfg['cobcrun']
            args = [QtCore.QFileInfo(path).completeBaseName()] + \
                cfg['run']['arguments']
        else:
            pgm = path
            args = cfg['run']['arguments']
        self.run_embedded(pgm, args, cfg, compiler_cfg, path)

    def enable_build_actions(self):
        path = api.editor.get_current_path()
        compilable = is_compilable(path)
        enable_build_actions = path is not None and compilable
        self.a_configure.setEnabled(enable_build_actions)
        self.a_build.setEnabled(enable_build_actions)
        self.a_clean.setEnabled(enable_build_actions)
        self.a_rebuild.setEnabled(enable_build_actions)
        if compilable:
            enable_build_actions &= 'run' in get_file_config(path)
        self.a_run.setEnabled(enable_build_actions)


class BuildThread(BuildThreadBase):
    def __init__(self, file_path):
        self.file_path = file_path
        self.abort = False
        super().__init__()

    def build(self):
        file_config = original_file_cfg = get_file_config(self.file_path)
        compiler_names = [get_file_compiler(self.file_path)] + \
            get_secondary_compilers(self.file_path)

        prefix = ''

        # preparse
        preparser = get_preparser_for_file(self.file_path)
        if preparser:
            self.configuration_message.emit(
                'Executing preparser: %r' % preparser.config['name'])
            success = self.preparse(file_config, preparser, self.file_path)
            if not success or preparser.only_preparser:
                self.finished.emit(success)
                return
            else:
                # change config to use the preparser output and continue
                # normal build procedure.
                file_config = original_file_cfg.copy()
                abs_path = preparser.get_output_file_path(self.file_path)
                file_config['path'] = abs_path
            prefix = '\n'

        build_directories = []

        for compiler_config_name in compiler_names:
            original_config = get_compiler_config(compiler_config_name)
            # compile
            compiler = GnuCOBOLCompiler(self.setup_overrides(
                original_config.copy(), file_config, preparser))
            output = compiler.config['output-directory']
            self.configuration_message.emit(
                prefix + 'Running compiler configuration: %r' %
                compiler_config_name)

            if output in build_directories:
                self.configuration_skipped.emit(
                    'Compiler configuration %r skipped because the output '
                    'directory has already been used by a previous '
                    'configuration...' % compiler_config_name)
                continue

            build_directories.append(output)
            success = self.compile(file_config, compiler, file_config['path'],
                                   None)
            prefix = '\n'

        self.finished.emit(success)


class DlgConfigureFile(DlgConfigureBase):
    """
    Dialog that let user configure out to build and run their project.
    """
    def __init__(self, fpath, parent):
        super().__init__(parent, title='Configure file')
        self._update_flg = False
        self.fpath = fpath
        compiler = get_file_compiler(fpath)
        self.ui.combo_compilers.setCurrentText(compiler)
        self.ui.group_files.hide()
        self.ui.combo_compilers.currentIndexChanged.connect(
            self._update_current_config_display)
        self.ui.group_override_build_options.toggled.connect(
            self._udpate_overrides)
        self.ui.tabWidget.setTabIcon(0, api.special_icons.run_build())
        self.ui.tabWidget.setTabIcon(1, api.special_icons.run_icon())
        self._update_flg = True
        self._display_config(get_file_config(fpath))
        self._update_flg = False
        self.secondary_compilers = get_secondary_compilers(fpath)

    def _update_current_config_display(self, _):
        if self._update_flg is False:
            self._update_flg = True
            self._display_config(get_file_config(self.fpath))
            self._update_flg = False

    def _display_config(self, cfg):
        self.display_file_config(cfg, self.fpath)

    def get_config(self):
        """
        Update the configuration of the currently selected file.

        Read field values and store item data.
        """
        return self.get_current_config(None)

    @staticmethod
    def configure(fpath, parent):
        """
        Changes project configuration.

        :param fpath: path of the project to edit
        :param parent: parent widget of the dialog.

        :returns: True if dialog was accepted, False if dialog was rejected.
        """
        dlg = DlgConfigureFile(fpath, parent)
        if dlg.exec_() == dlg.Accepted:
            set_file_config(fpath, dlg.get_config())
            set_file_compiler(fpath, dlg.get_compiler())
            set_secondary_compilers(fpath, dlg.secondary_compilers)
            return True
        return False


def get_file_config(file_path):
    """
    Gets the file compiler configuration.
    """
    file_configs = json.loads(QtCore.QSettings().value(
        'cobol/file_configs', '{}'))
    try:
        cfg = file_configs[file_path]
    except KeyError:
        ftype = GnuCOBOLCompiler.get_file_type(file_path)
        if ftype == MODULE:
            cfg = DlgConfigureFile.DEFAULT_MODULE_CFG
        else:
            cfg = DlgConfigureFile.DEFAULT_EXECUTABLE_CFG
        cfg['compile-submodules'] = True
        set_file_config(file_path, cfg)
    cfg['path'] = file_path
    return cfg


def set_file_config(file_path, config):
    """
    Saves the file compiler configuration.
    """
    file_configs = json.loads(QtCore.QSettings().value(
        'cobol/file_configs', '{}'))
    file_configs[file_path] = config
    QtCore.QSettings().setValue('cobol/file_configs',
                                json.dumps(file_configs))


def get_file_compiler(file_path):
    """
    Gets the name of the file's compiler configuration.

    :param file_path: file path.
    """
    file_compilers = json.loads(QtCore.QSettings().value(
        'cobol/file_compilers', '{}'))
    try:
        return file_compilers[file_path]
    except KeyError:
        name = DEFAULT_CONFIG_NAME
        set_file_compiler(file_path, name)
        return name


def set_file_compiler(file_path, name):
    """
    Saves the file's compiler config name

    :param name: name of the associated compiler config.
    :param file_path: file path
    """
    file_compilers = json.loads(QtCore.QSettings().value(
        'cobol/file_compilers', '{}'))
    file_compilers[file_path] = name
    QtCore.QSettings().setValue('cobol/file_compilers',
                                json.dumps(file_compilers))


def get_secondary_compilers(file_path):
    """
    Gets the list of secondary compiler for a given file path.

    :param file_path: file path

    :returns: the lisf of secondary compiler (names).
    """
    file_compilers = json.loads(QtCore.QSettings().value(
        'cobol/secondary_compilers', '{}'))
    try:
        compilers = file_compilers[file_path]
    except KeyError:
        set_secondary_compilers(file_path, [])
        compilers = []
    return [c for c in compilers if get_compiler_config(c) is not None]


def set_secondary_compilers(file_path, compiler_names):
    """
    Sets the list of secondary compiler for a given file path.

    :param file_path: file path
    """
    secondary_compilers = json.loads(QtCore.QSettings().value(
        'cobol/secondary_compilers', '{}'))
    secondary_compilers[file_path] = compiler_names
    QtCore.QSettings().setValue('cobol/secondary_compilers',
                                json.dumps(secondary_compilers))


def _logger():
    return logging.getLogger(__name__)
