from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.app.forms import dlg_select_workspaces_ui
from hackedit.app.workspaces import WorkspaceManager

from hackedit.app.dialogs.preferences import DlgPreferences


class DlgSelectWorkspace(QtWidgets.QDialog):
    def __init__(self, parent, app):
        self.app = app
        if QtGui.QIcon.hasThemeIcon('preferences-system-windows'):
            self.icon = QtGui.QIcon.fromTheme('preferences-system-windows')
        else:
            self.icon = QtGui.QIcon.fromTheme('applications-interfacedesign')
        super().__init__(parent)
        self.ui = dlg_select_workspaces_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.bt_ok = self.ui.buttonBox.button(self.ui.buttonBox.Ok)
        self.bt_edit = self.ui.buttonBox.button(self.ui.buttonBox.Apply)
        self.bt_edit.setText(_('Edit workspaces'))
        self._load_workspaces()
        self.ui.list_workspaces.itemSelectionChanged.connect(
            self._on_selection_changed)
        self.bt_edit.clicked.connect(self._edit_workspaces)

    def _load_workspaces(self):
        self.workspaces = WorkspaceManager()
        self.ui.list_workspaces.clear()
        names = self.workspaces.get_names()
        for name in names:
            item = QtWidgets.QListWidgetItem()
            item.setIcon(self.icon)
            item.setText(name)
            self.ui.list_workspaces.addItem(item)
        self.ui.list_workspaces.setCurrentRow(0)
        self._on_selection_changed()

    def _on_selection_changed(self):
        has_selected_item = len(self.ui.list_workspaces.selectedItems()) > 0
        self.bt_ok.setEnabled(has_selected_item)
        if has_selected_item:
            current_item = self.ui.list_workspaces.selectedItems()[0]
            w = self.workspaces.workspace_by_name(current_item.text())
            self.ui.lbl_description.setText(w['description'])
        else:
            self.ui.lbl_description.setText('')

    def _edit_workspaces(self):
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
        dlg = DlgPreferences(self, self.app)
        dlg.goto_page('Workspaces')
        QtWidgets.qApp.restoreOverrideCursor()
        if dlg.exec_() == dlg.Accepted:
            self._load_workspaces()

    @staticmethod
    def get_workspace(parent, app):
        dlg = DlgSelectWorkspace(parent, app)
        if dlg.exec_() == dlg.Accepted:
            return dlg.ui.list_workspaces.selectedItems()[0].text()
        return None
