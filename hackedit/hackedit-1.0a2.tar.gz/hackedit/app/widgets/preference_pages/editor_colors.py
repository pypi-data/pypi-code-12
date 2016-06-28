from PyQt5 import QtGui
from pyqode.core import modes, api

from hackedit.app import settings
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_editor_colors_ui


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


class EditorColors(PreferencePage):
    """
    Preference page for the application appearance settings (stylesheet, editor
    color scheme, font,...)
    """
    def __init__(self):
        icon = QtGui.QIcon.fromTheme('preferences-desktop-font')
        super().__init__(
            _('Font & Colors'), icon=icon, category=_('Editor'))
        self.ui = settings_page_editor_colors_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.edit_preview.modes.append(modes.CaretLineHighlighterMode())
        self.ui.edit_preview.modes.append(
            modes.PygmentsSH(self.ui.edit_preview.document()))
        self.ui.edit_preview.setPlainText(
            PREVIEW_TEXT, 'text/x-python', 'utf8')
        self.ui.combo_color_schemes.clear()
        styles = api.PYGMENTS_STYLES
        for custom_style in ['qt', 'darcula', 'aube', 'crepuscule',
                             'ark-dark']:
            if custom_style not in styles:
                styles.append(custom_style)
        for style in sorted(styles):
            self.ui.combo_color_schemes.addItem(style)
        self.ui.combo_color_schemes.currentIndexChanged.connect(
            self.update_preview)
        self.ui.fontComboBox.currentFontChanged.connect(self.update_preview)
        self.ui.spinbox_font_size.valueChanged.connect(self.update_preview)

    def reset(self):
        self.ui.fontComboBox.setCurrentFont(
            QtGui.QFont(settings.editor_font()))
        self.ui.spinbox_font_size.setValue(settings.editor_font_size())
        color_scheme = settings.color_scheme()
        self.ui.combo_color_schemes.setCurrentText(color_scheme)

    @staticmethod
    def restore_defaults():
        settings.set_editor_font('Hack')
        settings.set_editor_font_size(10)
        settings.set_color_scheme('qt')

    def save(self):
        settings.set_editor_font(self.ui.fontComboBox.currentFont().family())
        settings.set_editor_font_size(self.ui.spinbox_font_size.value())
        settings.set_color_scheme(self.ui.combo_color_schemes.currentText())

    def update_preview(self):
        cs = api.ColorScheme(self.ui.combo_color_schemes.currentText())
        self.ui.edit_preview.syntax_highlighter.color_scheme = cs
        font = self.ui.fontComboBox.currentFont().family()
        self.ui.edit_preview.font_size = self.ui.spinbox_font_size.value()
        self.ui.edit_preview.font_name = font
