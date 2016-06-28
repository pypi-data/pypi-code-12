"""
This module contains a series of widgets that you reuse in your plugins.
"""
import logging
import mimetypes
import os

import pkg_resources
from PyQt5 import QtGui, QtWidgets, QtCore, QtPrintSupport
from pygments.lexers.diff import DiffLexer
from pyqode.core import api, modes, panels
from pyqode.core.api import ColorScheme, utils
from pyqode.core.widgets import OutputWindow

from hackedit.app import settings
from hackedit.api import plugins, special_icons
from hackedit.app.forms import (
    dlg_progress_ui, dlg_run_process_ui, run_widget_ui,)
from hackedit.app.widgets.html_delegate import HTMLDelegate


def _logger():
    return logging.getLogger(__name__)


class PreferencePage(QtWidgets.QWidget):
    """
    Base class for implementing a preference page.

    A page is a widget whose name and icon will appear in the preferences
    tree view. If you want to add the page as a child page of a more
    top level node (what we call a category), set :attr:`category` to the
    name of the parent page (max depth = 1).
    """
    #: Specify whether the page can reset it ui to the initial settings.
    #: If false, the reset button will be hidden
    can_reset = True
    #: Specify whether the page can restore factory defaults. If False,
    #: the "Restore" button will be hidden
    can_restore_defaults = True
    #: Specify whether the page can apply settings. If False, the apply
    #: button will be hidden
    can_apply = True

    def __init__(self, name, icon=None, category=None):
        """
        :param name: Name of the page, as displayed in the tree view
        :param icon: Icon of the page (optional).
        :param category: Parent category (optional).
        """
        super().__init__()
        #: Name of the page
        self.name = name
        #: Icon of the page (QIcon)
        self.icon = icon
        #: Parent category, if any.
        self.category = category
        #: reference to the application
        self.app = None

    def reset(self):
        """
        Resets ui: QSettings -> GUI.
        """
        pass

    def restore_defaults(self):
        """
        Restore default settings in QSettings.
        """
        pass

    def save(self):
        """
        Saves changes: GUI -> QSettings.
        """
        pass


class DiffViewer(api.CodeEdit):
    """
    A simple diff viewer (read-only).
    """
    def __init__(self):
        super().__init__()
        self.show_context_menu = False
        self.sh = self.modes.append(modes.PygmentsSH(
            self.document(), DiffLexer()))
        self.lines = self.panels.append(
            panels.LineNumberPanel(), panels.LineNumberPanel.Position.LEFT)
        self.setReadOnly(True)
        self.syntax_highlighter.color_scheme = api.ColorScheme(
            settings.color_scheme())

    def setPlainText(self, txt):
        super().setPlainText(txt, mime_type='text/x-diff', encoding='utf-8')


class FindResultsWidget(QtWidgets.QTreeWidget):
    LIMIT = 1000

    @property
    def data_list(self):
        if self._data_list is None:
            self._compute_data_list()
        return self._data_list

    def __init__(self, parent=None, term='occurrences'):
        super().__init__(parent)
        self._data_list = None
        self.term = term
        self.setItemDelegate(HTMLDelegate())
        self.itemExpanded.connect(self._lazy_load_occurrences)

    @staticmethod
    def make_display_text(line_nbr, start, text, end):
        info_str = '(%d:%d) ' % (line_nbr + 1, start + 1)
        display_text = (
            '<i>' + info_str + '</i>' + text[:start] +
            '<span style="background-color: yellow; color: '
            'black"><b>' + text[start:end] + '</b></span>' +
            text[end:])
        return display_text
        # return '(%d:%d) %s ' % (line_nbr + 1, start + 1, text)

    def show_results(self, find_results, search_term):
        """
        Show the results of find in files.

        find_results is a list of tuple, each tuple is made up
        of the file path and the list of occurrences. The list of occurrences
        is a list of tuple made up of the line nbr, the line text and the list
        of occurrences (start/end) found on this line.
        """
        self.clear()
        self.setHeaderHidden(True)
        cpt_files, cpt_occurrences, first_item, root = self.fill_tree(
            find_results)
        if not cpt_occurrences:
            root.setText(0, _('No %s of "%s" found') % (
                self.term, search_term))
        else:
            root.setText(
                0, _('Found %d %s of "%s" in %d files') %
                (cpt_occurrences, self.term, search_term, cpt_files))
            root.setExpanded(True)
            root.child(0).setExpanded(True)
            self.setCurrentItem(root.child(0).child(0))

    def fill_tree(self, find_results):
        self._find_results = find_results
        cpt_occurrences = cpt_files = 0
        root = QtWidgets.QTreeWidgetItem()
        self.addTopLevelItem(root)
        first_item = None
        for path, occurrences in find_results:
            file_item = QtWidgets.QTreeWidgetItem()
            file_item.setIcon(0, FileIconProvider().icon(path))
            if not occurrences:
                continue
            root.addChild(file_item)
            occurrences_in_file = 0
            for line_nbr, text, line_occurrences in occurrences:
                cpt_occurrences += len(line_occurrences)
                occurrences_in_file += len(line_occurrences)
            file_item.setText(0, _('%s (%d occurrences)') % (
                path, occurrences_in_file))
            file_item.setChildIndicatorPolicy(file_item.ShowIndicator)
            file_item.setData(0, QtCore.Qt.UserRole, (path, occurrences))
            cpt_files += 1
        return cpt_files, cpt_occurrences, first_item, root

    def select_first_result(self):
        first_file = self.topLevelItem(0).child(0)
        if first_file:
            item = first_file.child(0)
            self.scrollTo(self.indexFromItem(item))
            item.setSelected(True)

    def _lazy_load_occurrences(self, file_item):
        assert isinstance(file_item, QtWidgets.QTreeWidgetItem)
        if file_item.childCount():
            # already loaded
            return
        path, occurrences = file_item.data(0, QtCore.Qt.UserRole)
        for line_nbr, text, line_occurrences in occurrences:
            for start, end in line_occurrences:
                item = QtWidgets.QTreeWidgetItem()
                display_text = self.make_display_text(
                    line_nbr, start, text, end)
                data = {
                    'path': path,
                    'line': line_nbr,
                    'start': start,
                    'end': end,
                    'text': text
                }
                item.setText(0, display_text)
                item.setData(0, QtCore.Qt.UserRole, data)
                file_item.addChild(item)

    def _compute_data_list(self):
        self._data_list = []
        for path, occurrences in self._find_results:
            for line_nbr, text, line_occurrences in occurrences:
                for start, end in line_occurrences:
                    self._data_list.append({
                        'path': path,
                        'line': line_nbr,
                        'start': start,
                        'end': end,
                        'text': text
                    })


class RunWidget(QtWidgets.QWidget):
    """
    Generic interface for running a program.
    """
    last_tab_closed = QtCore.pyqtSignal()

    stop_requested = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, window=None):
        super().__init__()
        self._interactive = True  # set to false when running tests
        self.main_window = window
        self.ui = run_widget_ui.Ui_Form()
        self.ui.setupUi(self)
        self.icon_unlock = special_icons.object_unlocked()
        self.icon_lock = special_icons.object_locked()
        self.icon_stop = QtGui.QIcon.fromTheme('process-stop')
        self.icon_run = special_icons.run_icon()
        self._tabs = []
        self.ui.bt_run.setIcon(special_icons.run_icon())
        self.ui.bt_clear.setIcon(QtGui.QIcon.fromTheme('edit-clear'))
        self.ui.bt_print.setIcon(QtGui.QIcon.fromTheme('document-print'))
        self.ui.tabWidget.currentChanged.connect(self._on_tab_changed)
        self.ui.bt_pin.clicked.connect(self._pin)
        self.ui.bt_run.clicked.connect(self._run)
        self.ui.bt_clear.clicked.connect(self._clear)
        self.ui.bt_print.clicked.connect(self._print)
        self.ui.tabWidget.setTabsClosable(True)
        self.ui.tabWidget.tabCloseRequested.connect(
            self._on_tab_close_requested)
        self.ui.bt_run.setEnabled(False)
        self.ui.bt_pin.setEnabled(False)
        self.ui.bt_print.setEnabled(False)
        self.ui.bt_clear.setEnabled(False)

    def current_tab(self):
        return self.ui.tabWidget.currentWidget()

    def run_program(self, pgm, args=None, cwd=None, env=None,
                    klass=OutputWindow, name=None):
        """
        Runs a program in an interactive console.

        :param pgm: program to run
        :param args: program arguments
        :param cwd: working directory
        :param env: program environment.
        :param klass: interactive console class. Default is
            :class:`pyqode.core.widgets.OutputWindow.
        """
        if name is None:
            name = QtCore.QFileInfo(pgm).completeBaseName()
        tab = self._find_free_tab(klass, pgm)
        if tab is None:
            try:
                tab = klass()
            except TypeError:
                tab = klass(self.main_window)
            tab.pinned = False
            self._tabs.append(tab)
            self.ui.tabWidget.addTab(tab, name)
        else:
            self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(tab), name)
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(tab))
        tab.pgm = pgm
        tab.args = args
        tab.cwd = cwd
        tab.env = env
        tab.font_name = settings.editor_font()
        tab.font_size = settings.editor_font_size()
        tab.start_process(pgm, arguments=args, working_dir=cwd, env=env, print_command=True)
        tab.process_finished.connect(self._on_process_finished)
        tab.identifier = pgm
        self.ui.bt_run.setIcon(self.icon_stop)
        self.ui.bt_run.setEnabled(True)
        self.ui.bt_pin.setEnabled(True)
        self.ui.bt_print.setEnabled(True)
        self.ui.bt_clear.setEnabled(True)
        try:
            self.parent().show()
        except AttributeError:
            pass
        return tab

    def apply_preferences(self):
        for i in range(self.ui.tabWidget.count()):
            w = self.ui.tabWidget.widget(i)
            w.font_name = settings.editor_font()
            w.font_size = settings.editor_font_size()

    def closeEvent(self, event):
        for i in reversed(range(self.ui.tabWidget.count())):
            self.ui.tabWidget.tabCloseRequested.emit(i)
        accept = self.ui.tabWidget.count() == 0
        event.setAccepted(accept)

    def _print(self):
        printer = QtPrintSupport.QPrinter()
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        dialog.setWindowTitle(_('Print run output'))
        if dialog.exec_() == dialog.Accepted:
            tab = self._tabs[self.ui.tabWidget.currentIndex()]
            tab.document().print(printer)

    def _clear(self):
        tab = self._tabs[self.ui.tabWidget.currentIndex()]
        tab.clear()

    def _run(self):
        tab = self._tabs[self.ui.tabWidget.currentIndex()]
        if tab.is_running:
            self.stop_requested.emit(tab)
            tab.stop_process()
            self.ui.bt_run.setIcon(self.icon_run)
        else:
            try:
                self.main_window.save_all()
            except AttributeError:
                pass  # _window is None, e.g. in test suite
            tab.start_process(tab.pgm, arguments=tab.args, working_dir=tab.cwd, env=tab.env,
                              print_command=True)
            self.ui.bt_run.setIcon(self.icon_stop)

    def _rm_tab(self, index):
        tab = self.ui.tabWidget.widget(index)
        self.ui.tabWidget.removeTab(index)
        tab.close()
        self._tabs.pop(index)

    def _on_tab_close_requested(self, index):
        try:
            tab = self._tabs[index]
        except IndexError:
            return
        if tab.is_running and self._interactive:
            if QtWidgets.QMessageBox.question(
                    self, _('Process running'),
                    _('A process is still running, do you want to terminate it'
                      ' now?'),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                tab.stop_process()
        self._rm_tab(index)
        if self.ui.tabWidget.count() == 0:
            self.last_tab_closed.emit()

    def _pin(self):
        tab = self._tabs[self.ui.tabWidget.currentIndex()]
        tab.pinned = self.ui.bt_pin.isChecked()
        self.ui.bt_pin.setIcon(self.icon_unlock if tab.pinned else
                               self.icon_lock)
        self.ui.bt_pin.setToolTip(
            _('Unlock current tab') if tab.pinned else _('Lock current tab'))

    def _on_tab_changed(self, index):
        if index >= 0:
            tab = self._tabs[index]
            self.ui.bt_pin.setChecked(tab.pinned)
            self.ui.bt_run.setIcon(
                self.icon_stop if tab.is_running else self.icon_run)
            self.ui.bt_pin.setIcon(
                self.icon_unlock if tab.pinned else self.icon_lock)
            self.ui.bt_pin.setToolTip(
                _('Unlock current tab') if tab.pinned else
                _('Lock current tab'))

    def _on_process_finished(self):
        self._on_tab_changed(self.ui.tabWidget.currentIndex())

    def _find_free_tab(self, klass, identifier):
        """
        Finds the first free tab (i.e. not running and not pinned).

        :param klass: requested tab class
        :return: QWidget or None
        """
        for tab in self._tabs:
            if (not tab.is_running and not tab.pinned and
                    type(tab) == klass and tab.identifier == identifier):
                return tab
        return None


class DlgProgress(QtWidgets.QDialog):
    """
    Shows background task progress and let the user cancel the background task.
    """
    #: Signal emitted when the user want to cancel the background operation.
    cancel_requested = QtCore.pyqtSignal()

    def __init__(self, parent=None, show_cancel_button=True):
        super().__init__(parent)
        self._ui = dlg_progress_ui.Ui_Dialog()
        self._ui.setupUi(self)
        self.progress_bar = self._ui.progressBar
        self.label = self._ui.label
        self._ui.pushButton.setVisible(show_cancel_button)
        self._ui.pushButton.clicked.connect(self.cancel_requested.emit)

    def set_progress(self, value):
        """
        Set the progress of the background task.

        :param value: the progress value [0-100], Use -1 for indeterminate.
        """
        if value == -1:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(value)

    def set_message(self, message):
        """
        Sets the message shown in the label.
        """
        self.label.setText(message)


class FileIconProvider(QtWidgets.QFileIconProvider):
    """
    Provides file/folder icons based on their mimetype.

    To extend this class, just create a FileIconProviderPlugin
    """
    plugins = []

    @classmethod
    def load_plugins(cls):
        """
        Loads FileIconProviderPlugins.
        """
        _logger().debug('loading icon provider plugins')
        for entrypoint in pkg_resources.iter_entry_points(
                plugins.FileIconProviderPlugin.ENTRYPOINT):
            _logger().debug('  - loading plugin: %s', entrypoint)
            try:
                plugin = entrypoint.load()
            except ImportError:
                _logger().exception('Failed to load plugin because of a '
                                    'missing a dependency')
            else:
                cls.plugins.append(plugin())

    @staticmethod
    def mimetype_icon(path, fallback=None):
        """
        Tries to create an icon from theme using the file mimetype.

        E.g.::

            return self.mimetype_icon(
                path, fallback=':/icons/text-x-python.png')

        :param path: file path for which the icon must be created
        :param fallback: fallback icon path (qrc or file system)
        :returns: QIcon
        """
        path = 'file.%s' % QtCore.QFileInfo(path).suffix()
        return _get_mimetype_icon(path, fallback)

    def icon(self, type_or_info):
        if isinstance(type_or_info, str):
            type_or_info = QtCore.QFileInfo(type_or_info)
        if isinstance(type_or_info, QtCore.QFileInfo):
            if type_or_info.isDir():
                return QtGui.QIcon.fromTheme('folder')
            else:
                for plugin in self.plugins:
                    ret_val = plugin.icon(type_or_info)
                    if ret_val is not None:
                        return ret_val
                # simplify path to help memoization
                simplified_path = 'file.%s' % type_or_info.suffix()
                return self.mimetype_icon(simplified_path)
        else:
            map = {
                FileIconProvider.File: QtGui.QIcon.fromTheme('text-x-generic'),
                FileIconProvider.Folder: QtGui.QIcon.fromTheme('folder'),
            }
            try:
                return map[type_or_info]
            except KeyError:
                return super().icon(type_or_info)


@utils.memoized
def _get_mimetype_icon(path, fallback):
    if 'CMakeLists.txt' in path:
        mime = 'text/x-cmake'
    else:
        mime = mimetypes.guess_type(path)[0]
    if mime:
        icon = mime.replace('/', '-')
        gicon = 'gnome-mime-%s' % icon
        has_icon = QtGui.QIcon.hasThemeIcon(icon)
        if QtGui.QIcon.hasThemeIcon(gicon) and not has_icon:
            return QtGui.QIcon.fromTheme(gicon)
        elif has_icon:
            return QtGui.QIcon.fromTheme(icon)
    if fallback:
        return QtGui.QIcon(fallback)
    return QtGui.QIcon.fromTheme('text-x-generic')


class DlgRunProcess(QtWidgets.QDialog):
    def __init__(self, parent=None, autoclose=False):
        super().__init__(parent)
        self.ui = dlg_run_process_ui.Ui_Dialog()
        self.autoclose = autoclose
        self.ui.setupUi(self)
        self.bt_cancel = self.ui.buttonBox.button(
            QtWidgets.QDialogButtonBox.Cancel)
        self.bt_close = self.ui.buttonBox.button(
            QtWidgets.QDialogButtonBox.Close)
        self.bt_close.setEnabled(False)
        self.bt_cancel.clicked.connect(self.cancel)
        self.ui.console.process_finished.connect(self.on_finished)

    def cancel(self):
        self.ui.console.stop_process()

    def on_finished(self):
        self.bt_cancel.setDisabled(True)
        self.bt_close.setEnabled(True)
        if self.autoclose:
            self.accept()

    @classmethod
    def run_process(cls, parent, program, arguments=[], cwd=None, env=None,
                    autoclose=False):
        dlg = cls(parent, autoclose=autoclose)
        dlg.setWindowTitle(_('Running %s %s') % (program, ' '.join(arguments)))
        dlg.ui.console.start_process(program, arguments=arguments, working_dir=cwd, env=env,
                                     print_command=True)
        ret = dlg.exec_()
        return dlg.ui.console.process.exitCode() == 0 and ret == cls.Accepted


class SpinnerLabel(QtWidgets.QLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dark = self.palette().base().color().lightness() < 255 / 2
        if dark or settings.dark_theme():
            self.movie = QtGui.QMovie(':/icons/special/spinner-dark.gif')
        else:
            self.movie = QtGui.QMovie(':/icons/special/spinner.gif')
        self.setMovie(self.movie)
        self.start = self.movie.start
        self.stop = self.movie.stop
        self.start()


class ClickableLabel(QtWidgets.QLabel):
    RICH_TEXT = '<html><head/><body><p><span style=" text-decoration: \
        underline; color:#3d8ec9;">%s</span></p></body></html>'

    clicked = QtCore.pyqtSignal()

    def __init__(self, text='', parent=None):
        super().__init__(self.RICH_TEXT % text, parent)
        self.setMouseTracking(True)

    def setText(self, text, rich=True):
        if rich:
            super().setText(self.RICH_TEXT % text)
        else:
            super().setText(text)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        QtWidgets.qApp.restoreOverrideCursor()
        self.clicked.emit()

    def enterEvent(self, ev):
        super().enterEvent(ev)
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.PointingHandCursor)

    def leaveEvent(self, ev):
        super().leaveEvent(ev)
        QtWidgets.qApp.restoreOverrideCursor()


class PathLineEdit(QtWidgets.QLineEdit):
    """
    Line edit specialised for choosing a path.

    Features:
        - use QCompleter with a QDirModel to automatically complete paths.
        - allow user to drop files and folders to set url text
    """
    class Completer(QtWidgets.QCompleter):
        def splitPath(self, path):
            path = path.split(os.pathsep)[-1]
            return super().splitPath(path)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        completer = self.Completer()
        model = QtWidgets.QDirModel(completer)
        model.setIconProvider(FileIconProvider())
        completer.setModel(model)
        self.setCompleter(completer)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            # for some reason, this doubles up the intro slash
            filepath = urls[0].path()
            self.setText(filepath)
            self.setFocus()


class ElidedLabel(QtWidgets.QLabel):
    """
    Label with text elision.
    """
    @property
    def elide_mode(self):
        return self._elide_mode

    @elide_mode.setter
    def elide_mode(self, mode):
        self._elide_mode = mode
        self.updateGeometry()

    def __init__(self, *args):
        super().__init__(*args)
        self._elide_mode = QtCore.Qt.ElideMiddle
        self._cached = ''

    def setText(self, txt):
        self._cache_elided_text(self.width())
        super().setText(txt)

    def _cache_elided_text(self, width):
        self._cached = self.fontMetrics().elidedText(self.text(), self.elide_mode, width - 10,
                                                     QtCore.Qt.TextShowMnemonic);

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._cache_elided_text(e.size().width())

    def paintEvent(self, e):
        if self._elide_mode == QtCore.Qt.ElideNone:
            super().paintEvent(e)
        else:
            p = QtGui.QPainter(self)
            p.drawText(0, 0, self.geometry().width(), self.geometry().height(), self.alignment(), self._cached)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    edit = PathLineEdit()
    edit.show()
    app.exec_()
