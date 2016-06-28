import os
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit import __version__
from hackedit.api.widgets import FileIconProvider
from hackedit.app import common
from hackedit.app.forms import welcome_window_ui


def _logger():
    return logging.getLogger(__name__)


class WelcomeWindow(QtWidgets.QMainWindow):
    """
    This is the welcome window. This is the first visible window when starting
    the application where you have access to the open/new actions and a list
    of recent files/projects.
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._ui = welcome_window_ui.Ui_MainWindow()
        self._ui.setupUi(self)
        self.setFixedSize(QtCore.QSize(865, 600))
        self.setWindowIcon(QtGui.QIcon.fromTheme(
            'hackedit', QtGui.QIcon(':/icons/hackedit_128.png')))
        self.setWindowTitle(_('Welcome'))
        self.app.get_recent_files_manager().updated.connect(
            self.update_recents)
        self.update_recents()
        self._ui.label_version.setText(_('Version %s') % __version__)
        self._ui.list_recents.remove_current_requested.connect(
            self.on_list_recents_remove_current_requested)
        self._ui.list_recents.clear_requested.connect(
            self.on_list_recents_clear_requested)
        self._ui.bt_quit.clicked.connect(self._quit)
        if not QtGui.QIcon.hasThemeIcon('application-exit'):
            self._ui.bt_quit.setIcon(QtGui.QIcon.fromTheme('window-close'))

        self._ui.bt_configure.clicked.connect(self._edit_preferences)

        a = QtWidgets.QAction(_('Help'), self)
        a.setToolTip(_('Get some help'))
        a.setIcon(QtGui.QIcon.fromTheme('system-help'))
        self._ui.bt_help.addAction(a)

        a = QtWidgets.QAction(_('About'), self)
        a.setToolTip(_('About HackEdit'))
        a.setIcon(QtGui.QIcon.fromTheme('help-about'))
        a.triggered.connect(self._show_about)
        self._ui.bt_help.addAction(a)

        sep = QtWidgets.QAction(self)
        sep.setSeparator(True)
        self._ui.bt_help.addAction(sep)

        a = QtWidgets.QAction(_('Report an issue...'), self)
        a.setIcon(QtGui.QIcon.fromTheme('tools-report-bug'))
        a.setToolTip(_('Create an issue (report a bug/enhancement)'))
        a.triggered.connect(self._report_bug)
        self._ui.bt_help.addAction(a)

        sep = QtWidgets.QAction(self)
        sep.setSeparator(True)
        self._ui.bt_help.addAction(sep)

        a = QtWidgets.QAction(_('Check for update'), self)
        a.setToolTip(_('Check for update'))
        a.setIcon(QtGui.QIcon.fromTheme('system-software-update'))
        a.triggered.connect(self._check_for_update)
        self._ui.bt_help.addAction(a)

        self._ui.bt_new.setFocus()

    def __repr__(self):
        return 'WelcomeWindow()'

    def closeEvent(self, event):
        super().closeEvent(event)
        self.app = None

    def showEvent(self, event):
        """ Shows the welcome window centered on the primary screen. """
        super().showEvent(event)
        _logger().debug('show centered')
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.size(),
                QtWidgets.qApp.desktop().availableGeometry()))

    @QtCore.pyqtSlot()
    def _quit(self):
        self.app.quit()

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_list_recents_itemClicked(self, item):
        """
        Opens the recent item.
        :param item: item to open
        """
        path = item.data(QtCore.Qt.UserRole)
        _logger().debug('recent item clicked: %r', path)
        self.app.open_path(path)

    @QtCore.pyqtSlot()
    def on_list_recents_remove_current_requested(self):
        """ Removes the currently selected recent file """
        filename = self._ui.list_recents.currentItem().data(
            QtCore.Qt.UserRole)
        _logger().debug('remove recent item requested: %r', filename)
        self.app.get_recent_files_manager().remove(filename)

    @QtCore.pyqtSlot()
    def on_list_recents_clear_requested(self):
        """ Clears the list of recent files """
        _logger().debug('clear recents requested')
        self.app.get_recent_files_manager().clear()

    @QtCore.pyqtSlot()
    def on_bt_new_clicked(self):
        common.create_new(self.app, self)

    @QtCore.pyqtSlot()
    def on_bt_open_clicked(self):
        """ Opens a file """
        _logger().debug('bt_open clicked')
        common.open_folder(None, self.app)

    @QtCore.pyqtSlot()
    def update_recents(self):
        """
        Updates the recent files list.
        """
        _logger().debug('update recent files list')
        if self.app is None:
            self.sender().updated.disconnect(self.update_recents)
            return
        self._ui.list_recents.clear()
        for file in self.app.get_recent_files_manager().get_recent_files():
            item = QtWidgets.QListWidgetItem()
            if os.path.ismount(file):
                item.setText(file)
            else:
                item.setText(
                    '%s\n%s' % (QtCore.QFileInfo(file).fileName(), file))
            item.setIcon(FileIconProvider().icon(
                         QtCore.QFileInfo(file)))
            item.setToolTip(file)
            item.setData(QtCore.Qt.UserRole, file)
            self._ui.list_recents.addItem(item)

    @QtCore.pyqtSlot()
    def _show_about(self):
        common.show_about(self)

    @QtCore.pyqtSlot()
    def _report_bug(self):
        common.report_bug(self)

    @QtCore.pyqtSlot()
    def _edit_preferences(self):
        common.edit_preferences(self, self.app)

    @QtCore.pyqtSlot()
    def _check_for_update(self):
        common.check_for_update(self)
