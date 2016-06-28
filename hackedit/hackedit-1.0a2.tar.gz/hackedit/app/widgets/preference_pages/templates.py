import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.api.widgets import PreferencePage, FileIconProvider
from hackedit.app import templates
from hackedit.app.forms import settings_page_templates_ui
from hackedit.app.forms import dlg_add_template_source_ui


class Templates(PreferencePage):
    """
    A page for configuring general editor settings (settings that apply
    to any editor independently from the target language).
    """
    can_reset = False
    can_restore_defaults = False
    can_apply = False

    def __init__(self):
        icon = QtGui.QIcon.fromTheme('folder-templates')
        super().__init__(_('Templates'), icon=icon)
        self.ui = settings_page_templates_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.list_sources.currentItemChanged.connect(
            self.update_source_templates)
        self.ui.bt_rm_source.clicked.connect(self.rm_source)
        self.ui.bt_add_source.clicked.connect(self.add_source)
        self.update_sources()
        self.update_source_templates(self.ui.list_sources.currentItem())

    def update_sources(self):
        row = self.ui.list_sources.currentRow()
        if row == -1:
            row = 0
        self.ui.list_sources.clear()
        sources = templates.get_sources()
        if not sources:
            return
        for src in sources:
            item = QtWidgets.QListWidgetItem()
            item.setText(src['label'])
            item.setToolTip(src['path'])
            item.setIcon(QtGui.QIcon.fromTheme('folder-templates'))
            item.setData(QtCore.Qt.UserRole, src)
            self.ui.list_sources.addItem(item)
        self.ui.list_sources.setCurrentRow(row)

    def update_source_templates(self, item):
        if item is None:
            self.ui.edit_source_path.clear()
            self.ui.list_templates.clear()
            self.ui.group_details.setDisabled(True)
            self.ui.bt_rm_source.setDisabled(True)
        else:
            self.ui.group_details.setDisabled(False)
            self.ui.bt_rm_source.setDisabled(False)
            self.ui.list_templates.clear()
            label = item.text()
            for templ in templates.get_templates(source_filter=label):
                titem = QtWidgets.QListWidgetItem()
                titem.setText(templ['name'])
                titem.setToolTip(templ['description'])
                icon = 'folder-templates'
                try:
                    icon = templ['icon']
                except KeyError:
                    _logger().debug('no icon set for template %s:%s',
                                    label, templ)
                if icon.startswith(':') or os.path.exists(icon):
                    icon = QtGui.QIcon(icon)
                elif icon.startswith('file.'):
                    icon = FileIconProvider().icon(icon)
                else:
                    icon = QtGui.QIcon.fromTheme(icon)
                titem.setIcon(icon)
                self.ui.list_templates.addItem(titem)

    def rm_source(self):
        source = self.ui.list_sources.currentItem().text()
        answer = QtWidgets.QMessageBox.question(
            self, _('Remove source'), _('Are you sure you want to remove the '
                                        'source %r?') % source)
        if answer == QtWidgets.QMessageBox.Yes:
            QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
            templates.rm_source(source)
            QtWidgets.qApp.restoreOverrideCursor()
        self.update_sources()

    def add_source(self):
        label, url = DlgAddSource.add_source(self)
        if label and url:
            templates.add_source(label, url)
        self.update_sources()

    def reset(self):
        pass

    @staticmethod
    def restore_defaults():
        pass

    def save(self):
        pass


class DlgAddSource(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = dlg_add_template_source_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.edit_label.textChanged.connect(self.enable_ok)
        self.ui.edit_url.textChanged.connect(self.enable_ok)

    def enable_ok(self):
        bt = self.ui.buttonBox.button(self.ui.buttonBox.Ok)
        bt.setDisabled(
            not self.ui.edit_label.text() or not self.ui.edit_url.text())

    @staticmethod
    def add_source(parent):
        dlg = DlgAddSource(parent)
        if dlg.exec_() == dlg.Accepted:
            return dlg.ui.edit_label.text().strip(), \
                dlg.ui.edit_url.text().strip()
        return None, None


def _logger():
    return logging.getLogger(__name__)
