"""
This module implements the wizard used to create new project/files
"""
import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.api.widgets import FileIconProvider
from hackedit.app import templates
from hackedit.app.forms import wizard_new_ui


class WizardNew(QtWidgets.QWizard):
    def __init__(self, parent, current_project):
        super().__init__(parent)
        self.is_valid = False
        self.home_path = os.path.expanduser('~')
        if not current_project:
            current_project = self.home_path
        self.current_project = current_project
        self.ui = wizard_new_ui.Ui_Wizard()
        self.ui.setupUi(self)
        self.ui.list_sources.currentItemChanged.connect(self.update_templates)
        self.ui.tree_templates.currentItemChanged.connect(
            self.update_next_btn)
        self.ui.edit_prj_path.textChanged.connect(self.check_path)
        self.ui.bt_select_prj_path.clicked.connect(self._select_directory)
        self.update_sources()

    def update_sources(self):
        row = self.ui.list_sources.currentRow()
        if row == -1:
            row = 0
        self.ui.list_sources.clear()
        for src in templates.get_sources():
            item = QtWidgets.QListWidgetItem()
            item.setText(src['label'])
            item.setIcon(QtGui.QIcon.fromTheme('folder-templates'))
            item.setData(QtCore.Qt.UserRole, src)
            self.ui.list_sources.addItem(item)
        self.ui.list_sources.setCurrentRow(row)

    def validateCurrentPage(self):
        is_valid = self.is_valid
        if is_valid:
            if self.currentId() == 0:
                item = self.ui.tree_templates.currentItem()
                templ = item.data(0, QtCore.Qt.UserRole)
                if templ['category'] == 'File':
                    self.single_file = True
                    self.ui.edit_prj_path.setText(self.current_project)
                else:
                    self.single_file = False
                    self.ui.edit_prj_path.setText(self.home_path)
                self.template = templ
                self.label = self.ui.list_sources.currentItem().text()
            elif self.currentId() == 1:
                self.path = self.ui.edit_prj_path.text()
        return is_valid

    def update_templates(self, item):
        project_tree_node = self.ui.tree_templates.topLevelItem(0)
        files_tree_node = self.ui.tree_templates.topLevelItem(1)
        uncategorized_tree_node = self.ui.tree_templates.topLevelItem(2)

        for node in [project_tree_node, files_tree_node,
                     uncategorized_tree_node]:
            node.takeChildren()

        if item is None:
            self.ui.tree_templates.setEnabled(False)
        else:
            self.button(self.NextButton).setEnabled(True)
            self.ui.tree_templates.setEnabled(True)
            label = item.text()
            for templ in templates.get_templates(source_filter=label):
                name = templ['name']
                description = ''
                parent = uncategorized_tree_node
                icon = 'folder'
                name = templ['name']
                description = templ['description']
                cat = templ['category']
                try:
                    icon = templ['icon']
                except KeyError:
                    _logger().debug('no icon set for template %s:%s',
                                    label, templ)
                if cat == 'Project':
                    parent = project_tree_node
                elif cat == 'File':
                    parent = files_tree_node
                    if icon == 'folder':
                        icon = 'document'
                titem = QtWidgets.QTreeWidgetItem()
                titem.setText(0, name)
                titem.setToolTip(0, description)
                if icon.startswith(':') or os.path.exists(icon):
                    icon = QtGui.QIcon(icon)
                elif icon.startswith('file.'):
                    icon = FileIconProvider().icon(icon)
                else:
                    icon = QtGui.QIcon.fromTheme(icon)
                titem.setIcon(0, icon)
                titem.setData(0, QtCore.Qt.UserRole, templ)
                parent.addChild(titem)
        flg_select = False
        for node in [project_tree_node, files_tree_node,
                     uncategorized_tree_node]:
            node.setExpanded(True)
            if not flg_select and node.childCount():
                self.ui.tree_templates.setCurrentItem(node.child(0))
                flg_select = True
            node.setHidden(not node.childCount())

    def update_next_btn(self, item):
        self.is_valid = item is not None and item.data(
            0, QtCore.Qt.UserRole) is not None
        self.button(self.NextButton).setEnabled(self.is_valid)

    def check_path(self, path):
        ok = False
        message = ''
        if os.path.isdir(path):
            try:
                files = os.listdir(path)
            except OSError:
                files = []
            if not self.single_file and files:
                message = _('Directory is not empty')
            else:
                ok = True
        elif os.path.exists(path):
            message = _('Path does is not a directory')
        else:
            ok = True
        self.ui.lbl_prj_location_error.setHidden(ok)
        self.ui.lbl_prj_location_error.setText(message)
        self.is_valid = ok

    def _select_directory(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select directory', self.ui.edit_prj_path.text())
        if path:
            self.ui.edit_prj_path.setText(path)

    @staticmethod
    def get_parameters(parent=None, current_project=None):
        wizard = WizardNew(parent, current_project)
        if wizard.exec_() == wizard.Accepted:
            return wizard.label, wizard.template, wizard.path, \
                wizard.single_file
        return None, None, None, None


def _logger():
    return logging.getLogger(__name__)
