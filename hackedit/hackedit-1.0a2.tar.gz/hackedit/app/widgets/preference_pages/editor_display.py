from PyQt5 import QtGui

from hackedit.app import settings
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_editor_display_ui


class EditorDisplay(PreferencePage):
    """
    A page for configuring general editor settings (settings that apply
    to any editor independently from the target language).
    """
    def __init__(self):
        if QtGui.QIcon.hasThemeIcon('display'):
            icon = QtGui.QIcon.fromTheme('display')
        else:
            icon = QtGui.QIcon.fromTheme('preferences-other')
        super().__init__(
            _('Display'), icon=icon, category=_('Editor'))
        self.ui = settings_page_editor_display_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.cb_margin.toggled.connect(self.ui.spin_margin_pos.setEnabled)

    def reset(self):
        self.ui.cb_text_wrapping.setChecked(settings.text_wrapping())
        self.ui.cb_margin.setChecked(settings.right_margin())
        self.ui.spin_margin_pos.setValue(settings.margin_position() + 1)
        self.ui.cb_center_on_scoll.setChecked(settings.center_on_scroll())
        self.ui.cb_caret_cope.setChecked(settings.highlight_caret_scope())
        self.ui.cb_show_line_numbers.setChecked(
            settings.show_line_numbers_panel())
        self.ui.cb_show_folding.setChecked(settings.show_folding_panel())
        self.ui.cb_show_errors.setChecked(settings.show_errors_panel())
        self.ui.cb_show_global_errors.setChecked(settings.show_global_panel())
        self.ui.cb_show_whitespaces.setChecked(settings.show_whitespaces())
        self.ui.cb_caret_line.setChecked(settings.highlight_caret_line())
        self.ui.cb_parentheses.setChecked(settings.highlight_parentheses())

    @staticmethod
    def restore_defaults():
        settings.set_text_wrapping(False)
        settings.set_right_margin(True)
        settings.set_margin_position(119)
        settings.set_center_on_scroll(True)
        settings.set_highlight_caret_scope(False)
        settings.set_show_line_numbers_panel(True)
        settings.set_show_folding_panel(True)
        settings.set_show_errors_panel(True)
        settings.set_show_global_panel(True)
        settings.set_show_whitespaces(False)
        settings.set_highlight_caret_line(True)
        settings.set_highlight_parentheses(True)

    def save(self):
        settings.set_text_wrapping(self.ui.cb_text_wrapping.isChecked())
        settings.set_right_margin(self.ui.cb_margin.isChecked())
        settings.set_margin_position(self.ui.spin_margin_pos.value() - 1)
        settings.set_center_on_scroll(self.ui.cb_center_on_scoll.isChecked())
        settings.set_highlight_caret_scope(self.ui.cb_caret_cope.isChecked())
        settings.set_show_line_numbers_panel(
            self.ui.cb_show_line_numbers.isChecked())
        settings.set_show_folding_panel(self.ui.cb_show_folding.isChecked())
        settings.set_show_errors_panel(self.ui.cb_show_errors.isChecked())
        settings.set_show_global_panel(
            self.ui.cb_show_global_errors.isChecked())
        settings.set_show_whitespaces(self.ui.cb_show_whitespaces.isChecked())
        settings.set_highlight_caret_line(self.ui.cb_caret_line.isChecked())
        settings.set_highlight_parentheses(self.ui.cb_parentheses.isChecked())
