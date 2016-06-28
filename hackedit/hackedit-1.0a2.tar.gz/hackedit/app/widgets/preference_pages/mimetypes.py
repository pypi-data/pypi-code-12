from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.app import settings
from hackedit.api.widgets import PreferencePage
from hackedit.app import mime_types
from hackedit.app.forms import settings_page_mimetypes_ui


class Mimetypes(PreferencePage):
    """
    Preference page for the mimetypes editor.
    """
    def __init__(self):
        self._current_mime = None
        if QtGui.QIcon.hasThemeIcon(
                'preferences-desktop-filetype-association'):
            icon = QtGui.QIcon.fromTheme(
                'preferences-desktop-filetype-association')
        elif QtGui.QIcon.hasThemeIcon('file-manager'):
            icon = QtGui.QIcon.fromTheme('file-manager')
        else:
            icon = QtGui.QIcon.fromTheme('applications-libraries')
        super().__init__(_('Mimetypes'), icon=icon, category=_('Environment'))
        self.ui = settings_page_mimetypes_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.table_mimes.currentItemChanged.connect(self._show_extensions)
        self.ui.edit_filter.editingFinished.connect(self._filter)
        self.ui.edit_filter.prompt_text = _('Filter by pattern/mimetype')

    def _filter(self):
        filter_text = self.ui.edit_filter.text().lower()
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
        first_row = None
        for i in range(self.ui.table_mimes.rowCount()):
            name = self.ui.table_mimes.item(i, 0).text().lower()
            if not filter_text or filter_text in name or \
                    filter_text in mime_types.get_extensions(name):
                self.ui.table_mimes.showRow(i)
                if first_row is None:
                    first_row = i
            else:
                self.ui.table_mimes.hideRow(i)
        if first_row is not None:
            self.ui.table_mimes.selectRow(first_row)
        QtWidgets.qApp.restoreOverrideCursor()

    def reset(self):
        mimes = mime_types.get_supported_mimetypes()
        self.ui.table_mimes.clearContents()
        self.ui.table_mimes.setRowCount(len(mimes))
        for i, mime in enumerate(sorted(mimes)):
            name = mime_types.get_handler(mime).__name__
            while name.startswith('_'):
                name = name[1:]

            item = QtWidgets.QTableWidgetItem()
            item.setText(mime)
            self.ui.table_mimes.setItem(i, 0, item)

            item = QtWidgets.QTableWidgetItem()
            item.setText(name)
            self.ui.table_mimes.setItem(i, 1, item)

        self.ui.edit_ignored.setText(';'.join(settings.ignored_patterns()))
        self.ui.table_mimes.selectRow(0)

    @staticmethod
    def restore_defaults():
        mime_types.reset_custom_extensions()
        settings.set_ignored_patterns(settings.DEFAULT_IGNORE_PATTERNS)

    def save(self):
        if self._current_mime:
            exts = self.ui.edit_mime_extensions.text().split(';')
            mime_types.set_extensions(self._current_mime, exts)
        settings.set_ignored_patterns(
            self.ui.edit_ignored.text().split(';'))

    def _show_extensions(self, *_):
        if self._current_mime:
            exts = self.ui.edit_mime_extensions.text().split(';')
            mime_types.set_extensions(self._current_mime, exts)
        r = self.ui.table_mimes.currentRow()
        item = self.ui.table_mimes.item(r, 0)
        if item is not None:
            self._current_mime = item.text()
            exts = mime_types.get_extensions(self._current_mime)
            self.ui.edit_mime_extensions.setText(';'.join(exts))
        else:
            self._current_mime = None
