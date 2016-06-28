"""
Registers CobolCodeEdit to the application's tab widget.
"""
import logging
from PyQt5 import QtCore, QtGui
from pyqode.cobol.widgets import CobolCodeEdit as Base

from hackedit import api
from hackedit_cobol import pyqode_cobol_server
import hackedit_cobol.lib.preparsers
from hackedit_cobol.lib import linter
from hackedit_cobol.forms import preferences_editor_ui

_ = api.gettext.get_translation(package='hackedit-cobol')


api.utils.add_mimetype_extension('text/x-cobol', '*.cbl')
api.utils.add_mimetype_extension('text/x-cobol', '*.CBL')
api.utils.add_mimetype_extension('text/x-cobol', '*.lst')
api.utils.add_mimetype_extension('text/x-cobol', '*.LST')
api.utils.add_mimetype_extension('text/x-cobol', '*.pco')
api.utils.add_mimetype_extension('text/x-cobol', '*.PCO')
api.utils.add_mimetype_extension('text/x-cobol', '*.cpy')
api.utils.add_mimetype_extension('text/x-cobol', '*.CPY')
for cfg in hackedit_cobol.lib.preparsers.get_configs():
    for ext in cfg['associated-extensions']:
        api.utils.add_mimetype_extension('text/x-cobol', ext.upper())
        api.utils.add_mimetype_extension('text/x-cobol', ext.lower())


class CobolEditor(Base):
    def __init__(self, parent=None, color_scheme='qt'):
        super().__init__(parent, color_scheme)
        self.modes.append(linter.CobolLinterMode())

    def _start_server(self):
        self.backend.start(pyqode_cobol_server.__file__)


class CobolCodeEditPlugin(api.plugins.EditorPlugin):
    @staticmethod
    def get_editor_class():
        return CobolEditor

    @staticmethod
    def get_specific_preferences_page():
        return CobolEditorPreferences()

    @staticmethod
    def apply_specific_preferences(editor):
        editor.lower_case_keywords = not bool(int(QtCore.QSettings().value(
            'cobol/proposed_keywords', '1')))
        editor.comment_indicator = QtCore.QSettings().value(
            'cobol/comment_symbol', '*> ')
        for cfg in hackedit_cobol.lib.preparsers.get_configs():
            for ext in cfg['associated-extensions']:
                api.utils.add_mimetype_extension('text/x-cobol', ext.upper())
                api.utils.add_mimetype_extension('text/x-cobol', ext.lower())

        try:
            m = editor.modes.get('CommentsMode')
        except KeyError:
            _logger().warn('no CommentsMode on editor %r', editor)
        else:
            m.action.setShortcut(api.shortcuts.get(
               'Comment/undcomment', _('Comment/Uncomment'), 'Ctrl+/'))

        try:
            m = editor.modes.get('OffsetCalculatorMode')
        except KeyError:
            _logger().warn('no OffsetCalculatorMode on editor %r', editor)
        else:
            m.action.setShortcut(api.shortcuts.get(
                'Calculate PIC offsets', _('Calculate PIC offsets'),
                'Ctrl+Alt+Shift+O'))

        try:
            m = editor.modes.get('GoToDefinitionMode')
        except KeyError:
            _logger().warn('no GoToDefinitionMode on editor %r', editor)
        else:
            m.action_goto.setShortcut(api.shortcuts.get(
                'Goto assignments', _('Goto assignments'), 'F7'))


class CobolEditorPreferences(api.widgets.PreferencePage):
    def __init__(self):
        super().__init__(
            'COBOL', icon=QtGui.QIcon(':/icons/cobol-mimetype-big.png'))
        self.ui = preferences_editor_ui.Ui_Form()
        self.ui.setupUi(self)

    def reset(self):
        radios = [self.ui.rb_lower_case, self.ui.rb_upper_case]
        proposed_keywords = int(QtCore.QSettings().value(
            'cobol/proposed_keywords', '1'))
        radios[proposed_keywords].setChecked(True)
        self.ui.edit_comment.setText(
            QtCore.QSettings().value('cobol/comment_symbol', '*> '))

    @staticmethod
    def restore_defaults():
        QtCore.QSettings().setValue('cobol/comment_symbol', '*> ')
        QtCore.QSettings().setValue('cobol/proposed_keywords', '1')

    def save(self):
        QtCore.QSettings().setValue('cobol/comment_symbol',
                                    self.ui.edit_comment.text())
        QtCore.QSettings().setValue(
            'cobol/proposed_keywords',
            0 if self.ui.rb_lower_case.isChecked() else 1)


def _logger():
    return logging.getLogger(__name__)
