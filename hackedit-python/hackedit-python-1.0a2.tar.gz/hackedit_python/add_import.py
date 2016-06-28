"""
This module contains the auto import mode that is set on the python editor.
"""
from PyQt5 import QtWidgets
from pyqode.core.api import Mode, TextHelper
from hackedit import api


_ = api.gettext.get_translation(package='hackedit-python')


class AddImportMode(Mode):
    def __init__(self):
        super().__init__()
        self.action = None

    def on_state_changed(self, state):
        if self.action is None:
            self.action = QtWidgets.QAction(self.editor)
            self.action.setText(_('Add import'))
            self.action.setToolTip(_(
                'Add a new import statement at the top of the imports zone.'))
            self.action.setShortcut('Alt+Return')
            self.action.triggered.connect(self._auto_import)
        if state:
            self.editor.add_action(self.action, sub_menu='Python')
        else:
            self.editor.remove_action(self.action)

    def _auto_import(self):
        helper = TextHelper(self.editor)
        name = helper.word_under_cursor(select_whole_word=True).selectedText()
        if name:
            import_stmt = 'import %s' % name
        else:
            import_stmt = ''
        import_stmt, status = QtWidgets.QInputDialog.getText(
            self.editor, _('Add import'), _('Import statement:'),
            QtWidgets.QLineEdit.Normal, import_stmt)
        if status:
            sh = self.editor.syntax_highlighter
            line_number = sh.import_statements[0].blockNumber()
            for stmt in sh.import_statements:
                if stmt.text() == import_stmt:
                    # same import already exists
                    return
            l, c = helper.cursor_position()
            cursor = helper.goto_line(line_number)
            cursor.insertText(import_stmt + '\n')
            helper.goto_line(l + 1, c)
