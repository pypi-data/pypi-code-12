"""
This plugin show the list of open documents.
"""
import os
from hackedit import api

from PyQt5 import QtCore, QtGui, QtWidgets


class OpenDocuments(api.plugins.WorkspacePlugin):
    """ This plugin show the list of open documents. """
    def activate(self):
        self.list = QtWidgets.QListWidget()
        if QtGui.QIcon.hasThemeIcon('folder-documents'):
            icon = QtGui.QIcon.fromTheme('folder-documents')
        else:
            icon = api.widgets.FileIconProvider.mimetype_icon('file.txt')
        api.window.add_dock_widget(self.list, _('Documents'), icon=icon, area=QtCore.Qt.LeftDockWidgetArea)
        api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED, self._update)
        self.list.itemActivated.connect(self._on_item_activated)
        self.list.itemClicked.connect(self._on_item_activated)
        self.icon_provider = api.widgets.FileIconProvider()

    def _update(self, *_):
        self.list.clear()
        names = []
        paths = []
        for path in api.editor.get_all_paths():
            paths.append(path)
            finfo = QtCore.QFileInfo(path)
            name = finfo.fileName()
            names.append(name)
        current_index = 0
        for n, p in zip(names, paths):
            if names.count(n) > 1:
                n = os.path.join(QtCore.QFileInfo(os.path.dirname(p)).completeBaseName(), n)
            itm = QtWidgets.QListWidgetItem(
                self.icon_provider.icon(QtCore.QFileInfo(n)), n)
            itm.setToolTip(p)
            if p == api.editor.get_current_path():
                current_index = self.list.count()
            self.list.addItem(itm)
        self.list.setCurrentRow(current_index)

    @staticmethod
    def _on_item_activated(item):
        path = item.toolTip()
        api.editor.open_file(path)
