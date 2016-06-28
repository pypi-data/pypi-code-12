import json
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.api import system, special_icons
from hackedit.api.widgets import PreferencePage
from hackedit.app.forms import settings_page_workspaces_ui
from hackedit.app.workspaces import WorkspaceManager


class Workspaces(PreferencePage):
    can_reset = False
    can_restore_defaults = False
    can_apply = False

    def __init__(self):
        if QtGui.QIcon.hasThemeIcon('preferences-system-windows'):
            self.icon = QtGui.QIcon.fromTheme('preferences-system-windows')
        else:
            self.icon = QtGui.QIcon.fromTheme('applications-interfacedesign')
        super().__init__(_('Workspaces'), icon=self.icon)
        self.ui = settings_page_workspaces_ui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.list_workspaces.currentRowChanged.connect(
            self._display_workspace)
        self.ui.bt_add_workspace.clicked.connect(self._add_workspace)
        self.ui.bt_copy_workspace.clicked.connect(self._cpy_workspace)
        self.ui.bt_remove_workspace.clicked.connect(self._rm_workspace)
        self.ui.bt_add_plugin.clicked.connect(self._add_plugin)
        self.ui.bt_rm_plugin.clicked.connect(self._rm_plugin)
        self.ui.list_available_plugins.currentRowChanged.connect(
            self._update_transfer_buttons)
        self.ui.list_used_plugins.currentRowChanged.connect(
            self._update_transfer_buttons)
        self.ui.edit_name.editingFinished.connect(
            self._on_name_changed)
        self.ui.edit_description.editingFinished.connect(
            self._on_description_changed)

    def reset(self):
        self.wm = WorkspaceManager()
        self.ui.list_workspaces.clear()
        for workspace in self.wm.get_names():
            item = QtWidgets.QListWidgetItem()
            item.setText(workspace)
            item.setIcon(self.icon)
            item.setToolTip(self.wm.workspace_by_name(
                workspace)['description'])
            self.ui.list_workspaces.addItem(item)
        self.ui.list_workspaces.setCurrentRow(0)

    @QtCore.pyqtSlot()
    def _add_workspace(self, *_, content=None):
        if content is None:
            content = {
                'name': '',
                'description': '',
                'plugins': [
                ]
            }
        name, _ = self._get_new_name(content['name'])
        if name is None:
            return  # cancel
        content['name'] = name
        self._save_workspace(content)
        self.reset()
        self._show_workspace(name)

    @QtCore.pyqtSlot()
    def _cpy_workspace(self):
        self._add_workspace(content=self._get_current_workspace().copy())

    @QtCore.pyqtSlot()
    def _rm_workspace(self):
        w = self._get_current_workspace()
        a = QtWidgets.QMessageBox.question(
            self, _('Confirm delete workspace'),
            _('Are you sure you want to remove workspace %r?') % w['name'])
        if a == QtWidgets.QMessageBox.Yes:
            os.remove(w['path'])
            self.reset()

    @QtCore.pyqtSlot()
    def _add_plugin(self):
        to_add = self.ui.list_available_plugins.currentItem().text()
        w = self._get_current_workspace()
        w['plugins'].append(to_add)
        self._save_workspace(w)
        self.reset()
        self._show_workspace(w['name'])

    @QtCore.pyqtSlot()
    def _rm_plugin(self):
        to_remove = self.ui.list_used_plugins.currentItem().text()
        w = self._get_current_workspace()
        w['plugins'].remove(to_remove)
        self._save_workspace(w)
        self.reset()
        self._show_workspace(w['name'])

    def _on_description_changed(self):
        value = self.ui.edit_description.text()
        w = self._get_current_workspace()
        if w is None:
            return
        w['description'] = value
        self._save_workspace(w)
        self.reset()
        self._show_workspace(w['name'])

    def _on_name_changed(self):
        value = self.ui.edit_name.text()
        w = self._get_current_workspace()
        if w is None:
            return
        try:
            os.remove(w['path'])
        except OSError:
            pass
        w['name'] = value
        self._save_workspace(w)
        self.reset()
        self._show_workspace(w['name'])

    def _plugin_icon(self):
        return special_icons.class_icon()

    def _update_available_plugins(self, used_plugins):
        self.ui.list_available_plugins.clear()
        available = self.app.plugin_manager.workspace_plugins.keys()
        for p in sorted(available):
            if p not in used_plugins:
                item = QtWidgets.QListWidgetItem()
                item.setText(p)
                item.setToolTip(
                    self.app.plugin_manager.workspace_plugins[p].__doc__)
                item.setIcon(self._plugin_icon())
                self.ui.list_available_plugins.addItem(item)
        self.ui.list_available_plugins.setCurrentRow(0)

    def _update_used_plugins(self, used_plugins):
        self.ui.list_used_plugins.clear()
        for p in sorted(used_plugins):
            try:
                doc = self.app.plugin_manager.workspace_plugins[p].__doc__
            except KeyError as e:
                print('KeyError', e, self.app.plugin_manager.workspace_plugins)
            else:
                item = QtWidgets.QListWidgetItem()
                item.setText(p)
                item.setToolTip(doc)
                item.setIcon(self._plugin_icon())
                self.ui.list_used_plugins.addItem(item)
        self.ui.list_used_plugins.setCurrentRow(0)

    def _update_transfer_buttons(self):
        w = self._get_current_workspace()
        self.ui.bt_add_plugin.setEnabled(
            self.ui.list_available_plugins.count() > 0 and w['editable'] and
            self.ui.list_available_plugins.currentItem() is not None)
        self.ui.bt_rm_plugin.setEnabled(
            self.ui.list_used_plugins.count() > 0 and w['editable'] and
            self.ui.list_used_plugins.currentItem() is not None)

    def _display_workspace(self, *_):
        self._update_interface(self._get_current_workspace())

    def _update_interface(self, w):
        if w:
            self.ui.group_properties.setEnabled(True)
            used_plugins = w['plugins']
            self.ui.edit_name.setText(w['name'])
            self.ui.edit_description.setText(w['description'])
            self._update_used_plugins(used_plugins)
            self._update_available_plugins(used_plugins)
            self.ui.edit_name.setReadOnly(not w['editable'])
            self.ui.edit_description.setReadOnly(not w['editable'])
            self.ui.bt_remove_workspace.setEnabled(w['editable'])
            self.ui.label_read_only.setHidden(w['editable'])
            self._update_transfer_buttons()
        else:
            self.ui.group_properties.setEnabled(False)

    def _get_new_name(self, name):
        if name:
            name = 'Copy of %s' % name
        ok = False
        while not ok:
            name, status = QtWidgets.QInputDialog.getText(
                self, _('Add workspace'), _('Workspace name:'),
                QtWidgets.QLineEdit.Normal, name)
            if status:
                path = os.path.join(
                    system.get_user_workspaces_dir(), name.lower() + '.json')
                if os.path.exists(path):
                    QtWidgets.QMessageBox.warning(
                        self, _('Cannot create workspace'),
                        _('Cannot create workspace %s, a workspace with the '
                          'same name already exists.\n'
                          'Please choose another name!') % name)
                else:
                    ok = True
            else:
                name = None
                ok = True
                path = None
        return name, path

    def _get_current_workspace(self):
        if self.ui.list_workspaces.currentItem():
            wname = self.ui.list_workspaces.currentItem().text()
            w = self.wm.workspace_by_name(wname)
            return w
        return None

    def _show_workspace(self, name):
        for i in range(self.ui.list_workspaces.count()):
            if self.ui.list_workspaces.item(i).text() == name:
                self.ui.list_workspaces.setCurrentRow(i)
                break

    def _save_workspace(self, content):
        content = content.copy()
        path = os.path.join(
            system.get_user_workspaces_dir(),
            content['name'].lower() + '.json')
        for k in ['path', 'editable']:
            try:
                content.pop(k)
            except KeyError:
                pass
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, 'w') as f:
                json.dump(content, f)
        except OSError:
            print('failed to save workspace')
