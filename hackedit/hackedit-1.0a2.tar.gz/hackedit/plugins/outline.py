"""
This plugin shows the outline of the current document.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqode.core.api import CodeEdit
from pyqode.core.widgets import OutlineTreeWidget, PromptLineEdit

from hackedit import api
from hackedit.api import plugins, special_icons


class DocumentOutline(plugins.WorkspacePlugin):
    """
    Shows the outline of the current editor
    """
    preferred_position = 1

    def activate(self):
        self._widget = QtWidgets.QWidget()
        self._outline = OutlineTreeWidget(self.main_window)
        self._outline.setMinimumWidth(200)
        self._outline.sync_with_editor_changed.connect(self._on_sync_changed)
        self._edit_filter = PromptLineEdit(self._widget, 'Filter by name')
        self._edit_filter.textChanged.connect(self._on_filter_text_changed)
        self._edit_filter.button.setIcon(QtGui.QIcon.fromTheme('edit-clear'))
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._outline)

        self._widget_controls = QtWidgets.QWidget(self._widget)
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(self._edit_filter)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.bt_lock = QtWidgets.QToolButton(self._widget)
        self.bt_lock.setCheckable(True)
        self.bt_lock.setChecked(not self._outline.sync_with_editor)
        self.bt_lock.setToolTip(_('Lock view'))
        self.bt_lock.toggled.connect(self._on_sync_toggled)
        self.bt_lock.setIcon(api.special_icons.object_locked())
        controls_layout.addWidget(self.bt_lock)

        self._widget_controls.setLayout(controls_layout)
        layout.addWidget(self._widget_controls)
        layout.setContentsMargins(3, 3, 3, 3)
        self._widget.setLayout(layout)
        dock = api.window.add_dock_widget(
            self._widget, _('Outline'), special_icons.class_icon(),
            QtCore.Qt.RightDockWidgetArea)
        dock.hide()
        self.main_window.current_tab_changed.connect(
            self._on_current_tab_changed)
        self._outline.set_editor(None)

    def _on_current_tab_changed(self, tab):
        if isinstance(tab, CodeEdit):
            self._outline.set_editor(tab)
        else:
            self._outline.set_editor(None)

    def _on_filter_text_changed(self):
        text = self._edit_filter.text()
        items = self._outline.findItems(text, QtCore.Qt.MatchContains |
                                        QtCore.Qt.MatchRecursive)
        for i in range(self._outline.topLevelItemCount()):
            self._hide_recursively(self._outline.topLevelItem(i), text != '')

        for item in items:
            item.setHidden(False)
            parent = item.parent()
            while parent:
                parent.setHidden(False)
                parent = parent.parent()

    def _hide_recursively(self, top, hide):
        top.setHidden(hide)
        for i in range(top.childCount()):
            child = top.child(i)
            self._hide_recursively(child, hide)

    def _on_sync_changed(self, sync):
        self.bt_lock.setChecked(not sync)

    def _on_sync_toggled(self, toggled):
        with api.utils.block_signals(self.bt_lock):
            self.bt_lock.setIcon(
                api.special_icons.object_unlocked() if toggled else
                api.special_icons.object_locked())
            self._outline.sync_with_editor = not toggled
            self.bt_lock.setToolTip(
                _('Unlock view') if toggled else _('Lock view'))
