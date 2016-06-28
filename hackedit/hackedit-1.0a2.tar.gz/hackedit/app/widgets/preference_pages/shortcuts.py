from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.api import shortcuts
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_shortcuts_ui


class Shortcuts(PreferencePage):
    def __init__(self):
        super().__init__(
            _('Shortcuts'), icon=QtGui.QIcon.fromTheme(
                'preferences-desktop-keyboard'), category=_('Environment'))
        self._ui = settings_page_shortcuts_ui.Ui_Form()
        self._ui.setupUi(self)
        self._ui.edit_filter.prompt_text = _('Filter by name or by shortcut')
        self._ui.edit_filter.textChanged.connect(self._filter)
        header_view = self._ui.table.horizontalHeader()
        header_view.setSectionResizeMode(0, header_view.Stretch)
        header_view.setSectionResizeMode(1, header_view.Interactive)

    def _filter(self, filter_text):
        filter_text = filter_text.lower()
        for i in range(self._ui.table.rowCount()):
            name = self._ui.table.item(i, 0).text().lower()
            sequence = QtGui.QKeySequence(filter_text).toString().lower()
            shortcut = self._ui.table.cellWidget(
                i, 1).keySequence().toString().lower()
            if not filter_text or filter_text in name or \
                    (sequence and sequence == shortcut):
                self._ui.table.showRow(i)
            else:
                self._ui.table.hideRow(i)

    def reset(self):
        # force refresh
        shortcuts.load()
        names = shortcuts.get_all_names()
        texts = shortcuts.get_all_texts()
        self._ui.table.clearContents()
        self._ui.table.setRowCount(len(names))
        for row, (action, text) in enumerate(zip(names, texts)):
            name_item = QtWidgets.QTableWidgetItem()
            name_item.setText(text)
            name_item.setData(QtCore.Qt.UserRole, action)
            self._ui.table.setItem(row, 0, name_item)
            edit = QtWidgets.QKeySequenceEdit()
            edit.setKeySequence(QtGui.QKeySequence(
                shortcuts.get(action, text, None)))
            edit.keySequenceChanged.connect(self.check_for_conflicts)
            edit.setObjectName(action)
            self._ui.table.setCellWidget(row, 1, edit)

    def check_for_conflicts(self, new_sequence):
        if not new_sequence.toString():
            return
        shortcuts = []
        names = []
        for i in range(self._ui.table.rowCount()):
            name = self._ui.table.item(i, 0).data(QtCore.Qt.UserRole)
            shortcut = self._ui.table.cellWidget(i, 1).keySequence().toString()
            shortcuts.append(shortcut)
            names.append(name)
        new_seq_str = new_sequence.toString()
        if shortcuts.count(new_seq_str) > 1:
            first_index = shortcuts.index(new_seq_str)
            second_index = shortcuts[first_index + 1:].index(new_seq_str)
            second_index += first_index + 1

            name = names[first_index]
            if name == self.sender().objectName():
                name = names[second_index]
            QtWidgets.QMessageBox.warning(
                self, _('Shortcuts conflict'),
                _('The shortcut %s is already used by action %r.\n'
                  'You will need to fix it otherwise both '
                  "shortcus won't work...") % (new_seq_str, name))

    @staticmethod
    def restore_defaults():
        shortcuts.restore_defaults()

    def save(self):
        for i in range(self._ui.table.rowCount()):
            item = self._ui.table.item(i, 0)
            name = item.data(QtCore.Qt.UserRole)
            text = item.text()
            shortcut = self._ui.table.cellWidget(i, 1).keySequence().toString()
            shortcuts.update(name, text, shortcut)
        shortcuts.save()
