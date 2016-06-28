from PyQt5 import QtCore, QtGui, QtWidgets


class RecentFilesListWidget(QtWidgets.QListWidget):
    """
    A custom list widget which keeps track of the mouse button that is
    pressed. It also changes the mouse cursor to a pointing hand cursor
    when the mouse cursor is over a list item.

    This class is used in QHomeWidget to ignore itemClicked when the right
    button is pressed.
    """
    remove_current_requested = QtCore.pyqtSignal()
    clear_requested = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pt):
        """
        Shows the recent files list context menu which allow to remove an item
        from the list or to clear the entire list.
        """
        action_remove = QtWidgets.QAction(
            _('Remove from recent files list'), self)
        action_remove.setToolTip(_('Remove path from recent files list'))
        action_clear = QtWidgets.QAction(
            _('Clear recent files list'), self)
        action_clear.setToolTip(
            _('Clear the recent files list'))
        action_remove.triggered.connect(self.remove_current_requested)
        action_clear.triggered.connect(self.clear_requested)
        action_clear.setIcon(QtGui.QIcon.fromTheme('edit-clear'))
        menu = QtWidgets.QMenu()
        menu.addAction(action_remove)
        menu.addAction(action_clear)
        menu.exec_(self.mapToGlobal(pt))

    def mousePressEvent(self, e):
        """
        Keeps track of the pressed button
        """
        self.mouseButton = e.button()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        """
        Display a pointing hand cursor when over an item. The cursor is
        reset to an ArrowCursor if there are no item under the cursor.
        """
        item = self.itemAt(e.pos())
        super().mouseMoveEvent(e)
        self.setCursor(QtCore.Qt.PointingHandCursor if item else
                       QtCore.Qt.ArrowCursor)
        if item:
            self.setCurrentRow(self.row(item))
