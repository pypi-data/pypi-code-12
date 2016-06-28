from PyQt5 import QtGui
from pyqode.core.managers import FileManager
from pyqode.core.modes import CodeCompletionMode

from hackedit.app import settings
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_editor_ui


class Editor(PreferencePage):
    """
    A page for configuring general editor settings (settings that apply
    to any editor independently from the target language).
    """
    def __init__(self):
        super().__init__(_('Editor'), icon=QtGui.QIcon.fromTheme(
            'accessories-text-editor'))
        self.ui = settings_page_editor_ui.Ui_Form()
        self.ui.setupUi(self)

    def reset(self):
        self.ui.spin_tab_len.setValue(settings.tab_length())
        self.ui.cb_spaces_instead_of_tabs.setChecked(
            settings.use_spaces_instead_of_tabs())
        self.ui.cb_convert_tabs_to_spaces.setChecked(settings.convert_tabs())
        self.ui.cb_clean_trailing.setChecked(
            settings.clean_trailing_whitespaces())
        self.ui.cb_restore_cursor.setChecked(settings.restore_cursor())
        self.ui.cb_safe_save.setChecked(settings.safe_save())
        self.ui.cb_encoding.current_encoding = settings.default_encoding()
        self.ui.cb_eol_convention.setCurrentIndex(settings.eol_convention())
        self.ui.cb_autodetect_eol.setChecked(settings.autodetect_eol())
        self.ui.spin_cc_trigger_len.setValue(settings.cc_trigger_len())
        self.ui.cb_cc_filter_mode.setCurrentIndex(settings.cc_filter_mode())
        self.ui.cb_cc_tooltips.setChecked(settings.cc_show_tooltips())
        self.ui.cb_cc_case_sensitive.setChecked(settings.cc_case_sensitive())
        self.ui.cb_autocomplete.setChecked(settings.auto_complete())
        self.ui.cb_autoindent.setChecked(settings.auto_indent())
        self.ui.cb_backspace_unindents.setChecked(
            settings.backspace_unindents())

    @staticmethod
    def restore_defaults():
        settings.set_tab_length(4)
        settings.set_use_spaces_instead_of_tabs(True)
        settings.set_convert_tabs(True)
        settings.set_clean_trailing_whitespaces(True)
        settings.set_restore_cursor(True)
        settings.set_safe_save(True)
        settings.set_default_encoding('UTF-8')
        settings.set_eol_convention(FileManager.EOL.System)
        settings.set_autodetect_eol(True)
        settings.set_cc_trigger_len(0)
        settings.set_cc_filter_mode(CodeCompletionMode.FILTER_FUZZY)  # subsequence filter mode
        settings.set_cc_show_tooltips(False)
        settings.set_cc_case_sensitive(False)
        settings.set_auto_complete(True)
        settings.set_auto_indent(True)
        settings.set_backspace_unindents(True)

    def save(self):
        settings.set_tab_length(self.ui.spin_tab_len.value())
        settings.set_use_spaces_instead_of_tabs(
            self.ui.cb_spaces_instead_of_tabs.isChecked())
        settings.set_convert_tabs(
            self.ui.cb_convert_tabs_to_spaces.isChecked())
        settings.set_clean_trailing_whitespaces(
            self.ui.cb_clean_trailing.isChecked())
        settings.set_restore_cursor(self.ui.cb_restore_cursor.isChecked())
        settings.set_safe_save(self.ui.cb_safe_save.isChecked())
        settings.set_default_encoding(self.ui.cb_encoding.current_encoding)
        settings.set_eol_convention(self.ui.cb_eol_convention.currentIndex())
        settings.set_autodetect_eol(self.ui.cb_autodetect_eol.isChecked())
        settings.set_cc_trigger_len(self.ui.spin_cc_trigger_len.value())
        settings.set_cc_filter_mode(self.ui.cb_cc_filter_mode.currentIndex())
        settings.set_cc_show_tooltips(self.ui.cb_cc_tooltips.isChecked())
        settings.set_cc_case_sensitive(
            self.ui.cb_cc_case_sensitive.isChecked())
        settings.set_auto_complete(self.ui.cb_autocomplete.isChecked())
        settings.set_auto_indent(self.ui.cb_autoindent.isChecked())
        settings.set_backspace_unindents(
            self.ui.cb_backspace_unindents.isChecked())
