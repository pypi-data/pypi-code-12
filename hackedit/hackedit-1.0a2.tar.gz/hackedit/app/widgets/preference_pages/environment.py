import os
import shlex

from PyQt5 import QtGui, QtWidgets
from pyqode.core.widgets import FileSystemContextMenu

from hackedit.api import system, gettext
from hackedit.api.widgets import PreferencePage
from hackedit.app import settings, environ, icons
from hackedit.app.forms import settings_page_environment_ui


PREVIEW_TEXT = '''@decorator(param=1)
def f(x):
    """ Syntax Highlighting Demo
        @param x Parameter"""
    s = ("Test", 2+3, {'a': 'b'}, x)   # Comment
    print s[0].lower()

class Foo:
    def __init__(self):
        self.makeSense(whatever=1)

    def makeSense(self, whatever):
        self.sense = whatever

x = len('abc')
print(f.__doc__)'''


class Environment(PreferencePage):
    """
    Preference page for the application appearance settings (stylesheet, editor
    color scheme, font,...)
    """
    def __init__(self):
        super().__init__(_('Environment'), icon=QtGui.QIcon.fromTheme(
            'applications-system'))
        self.ui = settings_page_environment_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        self.ui.combo_icon_themes.addItems(icons.icon_themes())
        self._reset_flg = False
        self.ui.bt_add.clicked.connect(self._add)
        self.ui.bt_remove.clicked.connect(self._remove)
        self.ui.table.itemSelectionChanged.connect(
            self._on_item_selection_changed)
        self._on_item_selection_changed()
        self.ui.cb_use_default_browser.stateChanged.connect(
            self.ui.edit_browser_command.setDisabled)
        self.ui.edit_file_manager.textChanged.connect(self._check_cmd)
        self.ui.edit_open_folder_in_terminal.textChanged.connect(
            self._check_cmd)
        self.ui.edit_run_command_in_terminal.textChanged.connect(
            self._check_cmd)
        self.ui.edit_browser_command.textChanged.connect(self._check_cmd)

        for lang_code in sorted(gettext.get_available_locales()):
            if lang_code == 'default':
                self.ui.combo_lang.addItem(_('default'), lang_code)
                continue
            try:
                # try to get lang display name with babel (if installed)
                from babel import Locale
                display = Locale(lang_code).display_name
            except ImportError:
                # babel not installed (optional dependency)
                display = lang_code
            self.ui.combo_lang.addItem(display, lang_code)

    def _check_cmd(self, *__, sender=None):
        if sender is None:
            sender = self.sender()
        try:
            pgm = shlex.split(sender.text(), posix=False)[0]
        except ValueError:
            pgm = sender.text().split(' ')[0]
        if system.which(pgm) is None:
            sender.setStyleSheet(
                'QLineEdit{background-color: #DD8080;color: white;}')
            sender.setToolTip(_('%s: command not found') % pgm)
        else:
            sender.setStyleSheet('')
            sender.setToolTip('')

    def _on_item_selection_changed(self):
        self.ui.bt_remove.setEnabled(len(self.ui.table.selectedItems()) > 0)

    def _add(self):
        self.ui.table.setRowCount(self.ui.table.rowCount() + 1)
        self.ui.table.selectRow(self.ui.table.rowCount() - 1)

    def _remove(self):
        itm = self.ui.table.selectedItems()[0]
        key = itm.text()
        self.ui.table.removeRow(self.ui.table.row(itm))
        try:
            os.environ.pop(key)
        except KeyError:
            pass

    def reset(self):
        self._reset_flg = True
        # user interface
        self.ui.cb_widescreen.setChecked(settings.widescreen_layout())
        self.ui.combo_theme.setCurrentIndex(int(settings.dark_theme()))
        self.ui.spin_toolbar_icon_size.setValue(settings.toolbar_icon_size())
        self.ui.combo_icon_themes.setCurrentText(settings.icon_theme())
        self.ui.cb_system_tray_icon.setChecked(settings.show_tray_icon())
        # system tools
        self.ui.edit_file_manager.setText(settings.file_manager_cmd())
        self.ui.edit_open_folder_in_terminal.setText(
            settings.get_cmd_open_folder_in_terminal())
        self.ui.edit_run_command_in_terminal.setText(
            settings.get_cmd_run_command_in_terminal())
        self.ui.cb_use_default_browser.setChecked(
            settings.use_default_browser())
        self.ui.edit_browser_command.setText(
            settings.get_custom_browser_command())
        for edit in [self.ui.edit_file_manager,
                     self.ui.edit_open_folder_in_terminal,
                     self.ui.edit_run_command_in_terminal,
                     self.ui.edit_browser_command]:
            self._check_cmd(sender=edit)
        # environment variables
        self.ui.table.clearContents()
        env = environ.load()
        keys = [k for k in sorted(env.keys())]
        self.ui.table.setRowCount(len(keys))
        for i, k in enumerate(keys):
            # key
            kitem = QtWidgets.QTableWidgetItem()
            kitem.setText(k)
            self.ui.table.setItem(i, 0, kitem)
            # value
            v = env[k]
            vitem = QtWidgets.QTableWidgetItem()
            vitem.setText(v)
            self.ui.table.setItem(i, 1, vitem)
        self.ui.table.resizeColumnsToContents()

        current_code = gettext.get_locale()
        for i in range(self.ui.combo_lang.count()):
            code = self.ui.combo_lang.itemData(i)
            if code == current_code:
                self.ui.combo_lang.setCurrentIndex(i)
                break
        self._reset_flg = False

    def restore_defaults(self):
        # user interface
        settings.set_widescreen_layout(False)
        settings.set_dark_theme(False)
        settings.set_use_system_icons(True if system.LINUX else False)
        settings.set_toolbar_icon_size(22)
        settings.set_icon_theme(icons.ORIGINAL_THEME_NAME if not system.LINUX
                                else 'default')
        # system tools
        FileSystemContextMenu._command = FileSystemContextMenu._explorer = None
        settings.set_file_manager_cmd(
            FileSystemContextMenu.get_file_explorer_command())
        settings.set_cmd_open_folder_in_terminal(
            system.get_cmd_open_folder_in_terminal())
        settings.set_cmd_run_command_in_terminal(
            system.get_cmd_run_command_in_terminal())
        settings.set_use_default_browser(True)
        settings.set_custom_browser_command('')
        settings.set_show_tray_icon(True)
        gettext.set_locale('default')
        # environment variables
        environ.restore()

    def save(self):
        # user interface
        settings.set_widescreen_layout(self.ui.cb_widescreen.isChecked())
        settings.set_dark_theme(bool(self.ui.combo_theme.currentIndex()))
        settings.set_toolbar_icon_size(self.ui.spin_toolbar_icon_size.value())
        settings.set_show_tray_icon(self.ui.cb_system_tray_icon.isChecked())
        settings.set_icon_theme(self.ui.combo_icon_themes.currentText())
        # system tools
        settings.set_file_manager_cmd(self.ui.edit_file_manager.text().strip())
        settings.set_cmd_open_folder_in_terminal(
            self.ui.edit_open_folder_in_terminal.text())
        settings.set_cmd_run_command_in_terminal(
            self.ui.edit_run_command_in_terminal.text())
        settings.set_use_default_browser(
            self.ui.cb_use_default_browser.isChecked())
        settings.set_custom_browser_command(
            self.ui.edit_browser_command.text())
        code = self.ui.combo_lang.currentData()
        if code != gettext.get_locale():
            QtWidgets.QMessageBox.information(
                self, _('Language changed'),
                _('You need to restart HackEdit for the new language to be '
                  'applied.'))

        gettext.set_locale(code)
        # environment variables
        env = {}
        for i in range(self.ui.table.rowCount()):
            itm = self.ui.table.item(i, 0)
            if itm:
                k = itm.text()
                itm = self.ui.table.item(i, 1)
                if itm:
                    v = itm.text()
                else:
                    v = ''
                env[k] = v
        environ.save(env)
        environ.apply()

    def _on_theme_changed(self):
        if self._reset_flg:
            return
        # change color scheme
        a = QtWidgets.QMessageBox.question(
            self, _('Change color scheme?'),
            _('Would you like to change the color scheme as well?'))
        dark = bool(self.ui.combo_theme.currentIndex())
        if a == QtWidgets.QMessageBox.Yes:
            scheme = 'crepuscule' if dark else 'aube'
            settings.set_color_scheme(scheme)
            self.colors.ui.combo_color_schemes.setCurrentText(scheme)
            self.colors.update_preview()

        # change icon theme (on Windows/OSX only).
        if not system.LINUX:
            a = QtWidgets.QMessageBox.question(
                self, _('Change icon theme?'),
                _('Would you like to change the icon theme as well?'))
            if a == QtWidgets.QMessageBox.Yes:
                theme = 'Breeze Dark' if dark else 'Breeze'
                self.ui.combo_icon_themes.setCurrentText(theme)
