import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.app import settings
from hackedit.app.forms import dlg_preferences_ui
from hackedit.app.widgets import preference_pages
from hackedit.api import system


def _logger():
    return logging.getLogger(__name__)


class DlgPreferences(QtWidgets.QDialog):
    _dlg = None

    closed = QtCore.pyqtSignal()

    color_highlight_background = None
    color_highlight_text = None

    def __init__(self, parent, app):
        super().__init__(parent)
        if DlgPreferences.color_highlight_background is None:
            DlgPreferences.color_highlight_background = \
                self.palette().color(QtGui.QPalette.Highlight).name()
        if DlgPreferences.color_highlight_text is None:
            DlgPreferences.color_highlight_text = self.palette().color(
                QtGui.QPalette.HighlightedText).name()
        self.app = app
        self._ui = dlg_preferences_ui.Ui_Dialog()
        self._ui.setupUi(self)
        self._connect_slots()
        # force reload of settings
        settings.load()
        self._setup_builtin_pages()
        self._setup_editor_pages()
        self._setup_plugin_pages()
        self._ui.categories.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self._ui.categories.expandAll()
        self.restore_state()
        btns = self._ui.buttons
        btns.button(btns.Reset).setToolTip(
            _('Reset changes made to the current page.'))
        btns.button(btns.RestoreDefaults).setToolTip(
            _('Restore factory defaults for the current page.'))
        btns.button(btns.Apply).setToolTip(
            _('Apply changes but keep dialog open.'))
        btns.button(btns.Ok).setToolTip(
            _('Apply changes and close dialog.'))
        btns.button(btns.Cancel).setToolTip(
            _('Close dialog and cancel any changes.'))
        self._ui.pages.setContentsMargins(0, 0, 0, 0)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.closed.emit()

    @staticmethod
    def edit_preferences(parent, app):
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
        dlg = DlgPreferences(parent, app)
        dlg.restore_state()
        QtWidgets.qApp.restoreOverrideCursor()
        if system.DARWIN:
            dlg.showMaximized()
        else:
            dlg.show()
        dlg.exec_()

    def goto_page(self, page_name):
        def get_page():
            for i in range(self._ui.categories.topLevelItemCount()):
                item = self._ui.categories.topLevelItem(i)
                if item.text(0) == page_name:
                    return item
                for j in range(item.childCount()):
                    child_item = item.child(j)
                    if child_item.text(0) == page_name:
                        return child_item
            return None
        item = get_page()
        self._ui.categories.setCurrentItem(item)

    def _find_item_by_index(self, index):
        for i in range(self._ui.categories.topLevelItemCount()):
            item = self._ui.categories.topLevelItem(i)
            idx = item.data(0, QtCore.Qt.UserRole)
            if idx == index:
                return item
            assert isinstance(item, QtWidgets.QTreeWidgetItem)
            for j in range(item.childCount()):
                child_item = item.child(j)
                idx = child_item.data(0, QtCore.Qt.UserRole)
                if idx == index:
                    return child_item
        return None

    def _on_item_activated(self, item):
        index = item.data(0, QtCore.Qt.UserRole)
        text = item.text(0)
        if item.parent() is not None:
            text = '%s - %s' % (item.parent().text(0), text)
        self._ui.label_title.setText(text)
        self._ui.label_title.setStyleSheet('''background-color: %s;
color: %s;
padding: 10px;
border-radius:3px;''' % (DlgPreferences.color_highlight_background,
                         DlgPreferences.color_highlight_text))
        self._ui.pages.setCurrentIndex(index)
        w = self._ui.pages.currentWidget()
        buttons = self._ui.buttons
        buttons.button(buttons.Reset).setVisible(w.can_reset)
        buttons.button(buttons.RestoreDefaults).setVisible(
            w.can_restore_defaults)
        buttons.button(buttons.Apply).setVisible(w.can_apply)

    def _reset(self):
        self._ui.pages.currentWidget().reset()

    def _restore_defaults(self):
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
        self._ui.pages.currentWidget().restore_defaults()
        self._reset()
        QtWidgets.qApp.restoreOverrideCursor()
        for i in range(self._ui.pages.count()):
            page = self._ui.pages.widget(i)
            page.save()

    def _apply(self):
        # save all settings
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            for i in range(self._ui.pages.count()):
                page = self._ui.pages.widget(i)
                page.save()
            self.app.apply_preferences()
            for i in range(self._ui.pages.count()):
                page = self._ui.pages.widget(i)
                page.reset()
        finally:
            QtWidgets.qApp.restoreOverrideCursor()

    def restore_state(self):
        index = int(QtCore.QSettings().value(
            '_cache/preferences_page_index', 0))
        item = self._find_item_by_index(index)
        self._ui.categories.setCurrentItem(item)

    def _setup_builtin_pages(self):
        env = preference_pages.Environment()
        self._add_page(env)
        self._add_page(preference_pages.Editor())

        self._add_page(preference_pages.Behaviour())
        colors = preference_pages.EditorColors()
        env.colors = colors
        self._add_page(colors)
        self._add_page(preference_pages.EditorDisplay())
        self._add_page(preference_pages.Indexing())
        self._add_page(preference_pages.Mimetypes())
        self._add_page(preference_pages.Notifications())
        self._add_page(preference_pages.Shortcuts())
        self._add_page(preference_pages.Templates())
        self._add_page(preference_pages.Workspaces())

    def _setup_plugin_pages(self):
        pages = []
        for p in self.app.plugin_manager.preferences_page_plugins:
            pages.append(p.get_preferences_page())
        for p in sorted(pages, key=lambda x: x.category is not None):
            self._add_page(p)
        pages[:] = []
        for p in self.app.plugin_manager.workspace_plugins.values():
            page = p.get_preferences_page()
            if page:
                pages.append(page)
        for p in sorted(pages, key=lambda x: x.category is not None):
            self._add_page(p)

    def _setup_editor_pages(self):
        for p in self.app.plugin_manager.editor_plugins:
            p = p.get_specific_preferences_page()
            if p:
                p.category = _('Editor')
                self._add_page(p)

    def _connect_slots(self):
        self._ui.categories.currentItemChanged.connect(
            self._on_item_activated)
        self._ui.buttons.button(self._ui.buttons.Reset).clicked.connect(
            self._reset)
        bt_restore_defaults = self._ui.buttons.button(
            self._ui.buttons.RestoreDefaults)
        bt_restore_defaults.clicked.connect(self._restore_defaults)
        self._ui.buttons.button(self._ui.buttons.Apply).clicked.connect(
            self._apply)

    def accept(self):
        self._apply()
        QtCore.QSettings().setValue(
            '_cache/preferences_page_index', self._ui.pages.currentIndex())
        super().accept()

    def reject(self):
        QtCore.QSettings().setValue(
            '_cache/preferences_page_index', self._ui.pages.currentIndex())
        super().reject()

    def _add_page(self, widget):
        """
        Adds a settings page to the dialog

        :param widget: page widget
        :type widget: hackedit.api.widgets.PreferencePage
        """
        if widget is None:
            return
        widget.setContentsMargins(0, 0, 0, 0)
        index = self._ui.pages.count()
        self._ui.pages.addWidget(widget)
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, widget.name)
        if widget.icon is not None:
            item.setIcon(0, widget.icon)
        item.setData(0, QtCore.Qt.UserRole, index)
        parent = None
        if widget.category:
            parent = self._ui.categories.findItems(
                widget.category, QtCore.Qt.MatchExactly, 0)
            if parent:
                parent = parent[0]
            else:
                print('parent not found', widget.category)
        if parent:
            parent.addChild(item)
        else:
            self._ui.categories.addTopLevelItem(item)
        widget.app = self.app
        widget.reset()

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Enter or \
                ev.key() == QtCore.Qt.Key_Return:
            return
        super().keyPressEvent(ev)
