"""
This module contains the preparsers preferences page and the function
to get/set the preparser configurations.

"""
import os

from PyQt5 import QtGui, QtWidgets

from hackedit import api
from hackedit_cobol.lib import dbpre, esql
from hackedit_cobol.forms import settings_page_preparsers_ui
from hackedit_cobol.lib.preparsers import DEFAULT_CONFIG, get_configs, \
    set_configs


_ = api.gettext.get_translation(package='hackedit-cobol')


CUSTOM_CONFIG_NAME = _('Custom')


class PreparserPreferencesPlugin(api.plugins.PreferencePagePlugin):
    @staticmethod
    def get_preferences_page():
        return PreparserPreferences()


class PreparserPreferences(api.widgets.PreferencePage):
    """
    Implements the preference page where the user can define the COBOL
    preparser configurations.
    """
    can_reset = False

    def __init__(self):
        if QtGui.QIcon.hasThemeIcon('database-index'):
            icon = QtGui.QIcon.fromTheme('database-index')
        else:
            icon = QtGui.QIcon.fromTheme('edit-find-replace')
        super().__init__(
            _('Preparsers'), icon=icon, category='COBOL')
        self.ui = settings_page_preparsers_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.bt_add_cfg.clicked.connect(self.add)
        self.ui.bt_rm_cfg.clicked.connect(self.remove)
        self.ui.combo_configs.currentIndexChanged.connect(
            self._display_config)
        self.ui.bt_parser_path.clicked.connect(self._select_parser_path)
        self._current_cfg = None

    def add(self):
        if api.system.WINDOWS:
            choices = [esql.NAME]
        else:
            choices = [dbpre.DBPRE_NAME]
        for i in range(self.ui.combo_configs.count()):
            to_remove = self.ui.combo_configs.itemText(i)
            if to_remove in choices:
                choices.remove(to_remove)
        choices.append(CUSTOM_CONFIG_NAME)
        if len(choices) > 1:
            item, status = QtWidgets.QInputDialog.getItem(
                self, _('Add preparser'),
                _('What kind of COBOL preparser would you like to add?'),
                choices, editable=False)
        else:
            item = CUSTOM_CONFIG_NAME
            status = True
        if status:
            config = self._get_initial_config(item)
            if config:
                configs = get_configs()
                configs.append(config)
                set_configs(configs)
                self.load_configs()
                self.ui.combo_configs.setCurrentIndex(
                    self.ui.combo_configs.findText(config['name']))

    def remove(self):
        name = self.ui.combo_configs.currentText()
        configs = get_configs()
        to_remove = None
        for cfg in configs:
            if cfg['name'] == name:
                to_remove = cfg
                break
        if to_remove:
            configs.remove(to_remove)
        set_configs(configs)
        self._current_cfg = None
        self.load_configs()

    def load_configs(self):
        self.ui.combo_configs.clear()
        for cfg in get_configs():
            i = self.ui.combo_configs.count()
            self.ui.combo_configs.addItem(cfg['name'])
            self.ui.combo_configs.setItemData(i, cfg)
        self.ui.group_config.setEnabled(self.ui.combo_configs.count() > 0)

    def _get_initial_config(self, item):
        forbidden_names = [
            self.ui.combo_configs.itemText(i)
            for i in range(self.ui.combo_configs.count())]
        if item == dbpre.DBPRE_NAME:
            # dbpre
            cfg = dbpre.DlgDbpreConfig.get_configuration(self)
        elif item == esql.NAME:
            # esql
            cfg = esql.get_esql_config(self)
        else:
            # Custom
            name, status = QtWidgets.QInputDialog.getText(
                self, _('Preparser configuration name'),
                _('Please, enter a name for the preparser configuration you '
                  'want to add: '))
            if not status:
                return None
            while name in forbidden_names:
                name = 'Copy of %s' % name
            cfg = DEFAULT_CONFIG.copy()
            cfg['name'] = name
        return cfg

    def _display_config(self, index):
        if self._current_cfg:
            self._save_current_cfg()
        if index != -1:
            cfg = get_configs()[index]
            self.ui.edit_extensions.setText(
                ' '.join(cfg['associated-extensions']))
            self.ui.edit_parser_path.setText(cfg['path'])
            self.ui.edit_cobol_compiler_flags.setText(
                cfg['extra-cobol-compiler-flags'])
            self.ui.edit_parser_flags.setText(cfg['flags'])
            self.ui.cb_only_preparser.setChecked(cfg['only-preparser'])
            self.ui.edit_output_rule.setText(cfg['output-rule'])
            self._current_cfg = cfg
        else:
            self.ui.edit_extensions.clear()
            self.ui.edit_parser_path.clear()
            self.ui.edit_cobol_compiler_flags.clear()
            self.ui.edit_parser_flags.clear()
            self.ui.cb_only_preparser.setChecked(False)
            self.ui.edit_output_rule.clear()
            self._current_cfg = None
        self.ui.bt_rm_cfg.setEnabled(index != -1)

    def _select_parser_path(self):
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Select preparser executable'),
            directory=self.ui.edit_parser_path.text())
        if path:
            self.ui.edit_parser_path.setText(os.path.normpath(path))

    def _save_current_cfg(self):
        cfg = self._current_cfg.copy()
        cfg['associated-extensions'] = [
            t for t in self.ui.edit_extensions.text().split(' ') if t]
        cfg['path'] = self.ui.edit_parser_path.text()
        cfg['extra-cobol-compiler-flags'] = \
            self.ui.edit_cobol_compiler_flags.text()
        cfg['flags'] = self.ui.edit_parser_flags.text()
        cfg['only-preparser'] = self.ui.cb_only_preparser.isChecked()
        cfg['output-rule'] = self.ui.edit_output_rule.text()
        configs = get_configs()
        if self._current_cfg in configs:
            configs.remove(self._current_cfg)
            configs.append(cfg)
            set_configs(configs)

    def reset(self):
        self.load_configs()
        self.ui.bt_add_cfg.setFocus()

    @staticmethod
    def restore_defaults():
        set_configs([])

    def save(self):
        if self._current_cfg:
            self._save_current_cfg()
