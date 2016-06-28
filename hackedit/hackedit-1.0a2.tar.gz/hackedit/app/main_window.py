"""
This module contains the main window implementation.

The main window is a windows with a set of preset objects (tab widget, file
system tree view) that is extended by plugins.
"""
import json
import traceback
import logging
import os

try:
    import psutil
except ImportError:
    psutil = None  # optional dependency.

from PyQt5 import QtCore, QtGui, QtPrintSupport, QtWidgets
from pyqode.core import modes, panels
from pyqode.core.api import TextHelper, ColorScheme, CodeEdit
from pyqode.core.widgets import EncodingsContextMenu, MenuRecentFiles
from pyqode.core.widgets import GenericCodeEdit, TextCodeEdit

from hackedit.app import settings
from hackedit.app.project import ProjectExplorer
from hackedit.api import system, shortcuts, special_icons
from hackedit.api.events import Event, WARNING, ExceptionEvent
from hackedit.api.project import load_user_config, save_user_config
from hackedit.api.widgets import ClickableLabel, FileIconProvider
from hackedit.app import common, events, generic_pyqode_server
from hackedit.app.dialogs.preferences import DlgPreferences
from hackedit.app.docks import DockWidgetsManager
from hackedit.app.forms import main_window_ui
from hackedit.app.tasks import TaskManagerWidget


def _logger():
    return logging.getLogger(__name__)


#: The editor page, which contains our splittable tab widget
PAGE_EDITOR = 0

#: Index of the page shown when no editor is open (show explanations about
#: how to open files in the IDE)
PAGE_EXPLANATIONS = 1


GenericCodeEdit.DEFAULT_SERVER = generic_pyqode_server.__file__
TextCodeEdit.DEFAULT_SERVER = generic_pyqode_server.__file__


class MainWindow(QtWidgets.QMainWindow):
    #: Signal emitted when window has been closed.
    closed = QtCore.pyqtSignal(QtWidgets.QMainWindow)
    current_tab_changed = QtCore.pyqtSignal(QtWidgets.QWidget)
    editor_created = QtCore.pyqtSignal(QtWidgets.QWidget)
    editor_detached = QtCore.pyqtSignal(QtWidgets.QWidget, QtWidgets.QWidget)
    editor_loaded = QtCore.pyqtSignal(QtWidgets.QWidget)
    project_added = QtCore.pyqtSignal(str)
    current_project_changed = QtCore.pyqtSignal(str)
    project_files_available = QtCore.pyqtSignal()
    about_to_open_tab = QtCore.pyqtSignal(str)
    document_saved = QtCore.pyqtSignal(str, str)
    state_restored = QtCore.pyqtSignal()
    file_renamed = QtCore.pyqtSignal(str, str)
    file_deleted = QtCore.pyqtSignal(str)

    @property
    def task_manager(self):
        """
        Gets the task manager instance.

        :return: hackedit.app.tasks.TaskManager
        """
        return self.task_manager_widget.task_manager

    @property
    def current_tab(self):
        """
        Gets the current tab (widget).

        :param self: parent window.
        :return: QWidget
        """
        return self._current_tab

    @property
    def projects(self):
        """
        Gets the list of open projects.

        Remember that when you open a single file, the IDE actually opens the
        parent folder instead and open the file in a new tab.

        :return: list of str
        """
        return self._open_projects

    @property
    def current_project(self):
        """
        Gets the current project/file path.
        :return: str
        """
        return self._current_folder

    @current_project.setter
    def current_project(self, value):
        self._current_folder = value

    @property
    def tab_widget(self):
        """
        Gets a reference to the main tab widget.
        :return: pyqode.core.widgets.SplittableCodeEditTabWidget
        """
        return self._ui.tabs

    @property
    def ui(self):
        return self._ui

    def __init__(self, app, path, workspace):
        """
        :param app: reference to the application instance
        :param path: main path (linked paths will be open automatically).
        """
        super().__init__()
        self.setAcceptDrops(True)
        self._docks_to_restore = []
        self._toolbars = []
        self._open_projects = []
        self._current_tab = None
        #: Reference to the application instance.
        self.app = app
        self.app.active_window = self
        #: List of plugins added to the window
        self.plugins = []
        #: Workspace definition
        self.workspace = workspace
        #: Dock widgets manager
        self._dock_manager = None
        #: List of dock widget currently displayed
        self._dock_widgets = []
        #: User interface definition
        self._ui = main_window_ui.Ui_MainWindow()
        self._ui.setupUi(self)
        self._ui.stackedWidget.setCurrentIndex(1)

        if not QtGui.QIcon.hasThemeIcon('application-exit'):
            self._ui.action_quit.setIcon(QtGui.QIcon.fromTheme('window-close'))

        self.addActions(self._ui.mnu_file.actions())
        self.addActions(self._ui.mnu_edit.actions())
        self.addActions(self._ui.mnu_help.actions())
        self.addActions(self._ui.mnu_view.actions())

        self.setWindowIcon(QtGui.QIcon.fromTheme(
            'hackedit', QtGui.QIcon(':/icons/hackedit_128.png')))
        self._setup_actions()

        #: Menus map
        self._menus = {
            'File': self._ui.mnu_file,
            'Edit': self._ui.mnu_edit,
            'View': self._ui.mnu_view,
            'Tools': self._ui.menuTools,
            '?': self._ui.mnu_help
        }
        self._menus_list = [
            self.ui.mnu_file,
            self._ui.mnu_edit,
            self._ui.menuTools,
            self._ui.mnu_view,
            self._ui.mnu_help
        ]
        # setup application menu button
        menu_button = QtWidgets.QToolButton(self)
        menu_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        menu_button.setIcon(special_icons.app_menu())
        menu_button.setToolTip('Application menu')
        self.menu_button = menu_button
        self._update_menu_button()

        # setup recent files menu
        self._mnu_recents = MenuRecentFiles(
            self._ui.mnu_file,
            recent_files_manager=self.app.get_recent_files_manager(),
            clear_icon=QtGui.QIcon.fromTheme('edit-clear'),
            icon_provider=FileIconProvider())
        self._mnu_recents.setTitle('Recents')
        self._mnu_recents.menuAction().setIcon(
            QtGui.QIcon.fromTheme('document-open-recent'))
        self._ui.mnu_file.insertMenu(self._ui.mnu_file.actions()[3],
                                     self._mnu_recents)
        self._current_folder = ''
        self._dock_manager = DockWidgetsManager(self)
        self._connect_slots()
        self.update_mnu_view()
        self.task_manager_widget = TaskManagerWidget(self)
        self.add_statusbar_widget(self.task_manager_widget)
        self._setup_status_bar_widgets()
        self.notifications = events.Manager(self)
        self.open_folder(path)
        self.project_explorer = ProjectExplorer(self)
        self.project_explorer.activate()
        self.project_explorer.apply_preferences()

        self._update_mem_label_timer = QtCore.QTimer()
        self._update_mem_label_timer.setInterval(500)
        self._update_mem_label_timer.timeout.connect(self._update_mem_label)
        self._update_mem_label_timer.start()
        self._update_mem_label()

    def setup_menu_toolbar(self):
        empty = QtWidgets.QWidget()
        empty.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                            QtWidgets.QSizePolicy.Preferred)
        self.toolbar_menu = QtWidgets.QToolBar(self)
        self.toolbar_menu.setObjectName('toolBarAppMenu')
        self.toolbar_menu.setMovable(False)
        self.toolbar_menu.addWidget(empty)
        self.toolbar_menu.addWidget(self.menu_button)
        self.addToolBar(self.toolbar_menu)
        self._update_menu_visibility()

    def __repr__(self):
        return 'MainWindow(path=%r)' % self.projects

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def open_folder(self, path):
        """
        Adds a path to the window.

        :param path: path to add: file or directory
        """
        if path in self.projects or not os.path.exists(path):
            # already open
            return
        _logger().debug('open folder: %r', path)
        self._open_projects.append(path)
        self.project_added.emit(path)
        self._current_folder = path
        linked_paths = self._get_linked_paths()
        if len(self.projects) > 1:
            # save the additional paths in project configs, that way
            # they will be open together next time.
            linked_paths.append(path)
            self._save_linked_paths(linked_paths)
        else:
            # read possible linked paths and open them
            for pth in linked_paths:
                self.open_folder(pth)
            self._save_linked_paths(linked_paths)
        self.on_current_tab_changed(None)
        hackedit_path = os.path.join(path, '.hackedit')
        try:
            os.makedirs(hackedit_path)
        except FileExistsError:
            _logger().debug('failed to create .hackedit folder at %r, '
                            'directory already exits', path)

    def remove_folder(self, path):
        try:
            self._open_projects.remove(path)
        except ValueError:
            _logger().warn('failed to remove folder %r', path)

    def get_menu(self, menu_name):
        """
        Gets a top level menu.

        The menu is implicitly created if it did not exist.

        :param self: window to get a QMenu from
        :param menu_name: Name of the menu to retrieve.

        :return: QtWidgets.QMenu
        """
        try:
            return self._menus[menu_name.replace('&', '')]
        except KeyError:
            # create a new menu.
            _logger().debug('creating menu %r on %r', menu_name, self)
            mnu = QtWidgets.QMenu(menu_name, self.menuBar())
            self.menuBar().insertMenu(self._menus['Tools'].menuAction(), mnu)
            self._menus[menu_name.replace('&', '')] = mnu

            tools_menu = self._menus['Tools']
            i = self._menus_list.index(tools_menu)
            self._menus_list.insert(i, mnu)
            self._update_menu_button()
            return mnu

    def get_toolbar(self, name, title):
        """
        Gets a toolbar.

        The toolbar is implicitly created if it did not exist.

        :param name: Name of the toolbar
        :param title: Title of the toolbar (used when creating the toobar).
        :return: QToolBar
        """
        children = self.findChildren(QtWidgets.QToolBar, name)
        if children:
            toolbar = children[0]
        else:
            toolbar = QtWidgets.QToolBar(title)
            toolbar.setObjectName(name)
            self.addToolBar(toolbar)
        return toolbar

    def add_dock_widget(self, widget, title, icon, area, special):
        """
        Add a dock widget to the window.

        You pass a widget that is automatically wrapped into a QDockWidget.

        :param self: window where the dock widget must be added
        :param widget: the widget to dock (QWidget, not a QDockWidget)
        :param title: dock widget title
        :param icon: dock widget icon. Default is None
        :param area: dock widget area. Default is bottom area
        :param no_button: True to avoid showing a button. Default is False

        :return The dock widget instance that was added to the window.
        """
        _logger().debug('adding dock widget %r to %r', title, self)

        class DockWidget(QtWidgets.QDockWidget):
            """
            Forces focus on the child widget when the dock is shown.
            """
            def showEvent(self, ev):
                super().showEvent(ev)
                self.widget().setFocus()

        if area is None:
            area = QtCore.Qt.BottomDockWidgetArea
        if system.PLASMA_DESKTOP:
            title = title.replace('&', '')
            title = title[:-1] + '&' + title[-1]
        dock = DockWidget(title, self)
        dock.setShortcutEnabled(False)
        dock.setObjectName('dock%s' % title)
        dock.setWidget(widget)
        if icon:
            dock.setWindowIcon(icon)
        dock.setShortcutEnabled(0, False)
        self.addDockWidget(area, dock, special=special)
        return dock

    def get_dock_widget(self, title):
        """
        Returns the dock widget whose windowTitle match `title`.

        :param self: parent window.
        :param title: title of the dock widget to get.
        :return: QDockWidget
        """
        for dock in self._dock_widgets:
            if dock.windowTitle().replace('&', '') == title:
                return dock
        return None

    def get_project_treeview(self):
        """
        Gets the project treeview.

        :return: pyqode.core.widgets.FileSystemTreeView
        """
        return self.project_explorer.view

    def open_file(self, path, line=None, column=0):
        """
        Opens a new tab in the window (and optionally goes to the
        specified line).

        :param path: path to open
        :param line: line to go to (optional).
        :param line: column to go to (optional).
        """
        if path is None:
            return
        path = os.path.normpath(path)
        if not os.path.exists(path) or os.path.isdir(path):
            return None
        self.about_to_open_tab.emit(path)
        color_scheme = settings.color_scheme()
        try:
            tab = self._ui.tabs.open_document(
                path, encoding=settings.default_encoding(),
                replace_tabs_by_spaces=settings.convert_tabs(),
                clean_trailing_whitespaces=settings.
                clean_trailing_whitespaces(),
                safe_save=settings.safe_save(),
                restore_cursor_position=settings.restore_cursor(),
                preferred_eol=settings.eol_convention(),
                autodetect_eol=settings.autodetect_eol(),
                show_whitespaces=settings.show_whitespaces(),
                color_scheme=color_scheme)
        except Exception as e:
            tab = None
            tb = traceback.format_exc()
            _logger().exception('failed to open file')
            self.notifications.add(ExceptionEvent(
                _('Failed to open file: %s') % path,
                _('An unhandled exception occured while opening file: %r') % e,
                e, tb=tb), show_balloon=False)
        else:
            _logger().debug('document opened: %s', path)

            try:
                tab.remove_action(tab.action_goto_line)
            except AttributeError:
                _logger().debug('cannot remove action goto line from editor '
                                '%r, not a CodeEdit', tab)
            else:
                assert isinstance(tab, CodeEdit)
                tab.add_action(self.project_explorer.action_goto_line)
            try:
                mode = tab.modes.get('FileWatcherMode')
            except (KeyError, AttributeError):
                _logger().debug('no file watcher on widget %r', tab)
            else:
                # enable filewatcher autoreload
                mode.auto_reload = True
            if line is not None:
                QtWidgets.qApp.processEvents()
                try:
                    TextHelper(tab).goto_line(line, column)
                except AttributeError:
                    _logger().debug('failed to go to line %d in %r' % (
                        line, tab.file.path))
        return tab

    def add_statusbar_widget(self, widget, with_separator=True, first=False):
        """
        Add a widget to the status bar.

        The associated widget action is set on the widget as "toolbar_action"

        :param widget: widget to add
        :param with_separator: true to add a separator before the widget
        :param first: True to add the widget at the beggining of the bar
            instead of the end.
        :return: the associated widget action (use it for show/hide).
        """
        action = self._dock_manager.add_bottom_widget(
            widget, with_separator, first)
        widget.toolbar_action = action
        return action

    def get_plugin_instance(self, plugin_class):
        """
        Returns the plugin instance that match a given plugin class.

        :param self: parent window
        :param plugin_class: Plugin class
        """
        for p in self.plugins:
            if isinstance(p, plugin_class):
                return p
        return None

    def save_current(self):
        """
        Saves the current tab.
        """
        try:
            self._ui.tabs.save_current()
        except Exception as e:
            self.notifications.add(Event(
                _('Failed to save file'), str(e), level=WARNING),
                show_balloon=False)

    def save_current_as(self):
        """
        Saves the current tab as.
        """
        try:
            self._ui.tabs.save_current_as()
        except Exception as e:
            self.notifications.add(Event(
                _('Failed to save file'), str(e), level=WARNING),
                show_balloon=False)
        else:
            self.update_title()

    def save_all(self):
        """
        Saves all open tabs
        """
        try:
            self._ui.tabs.save_all()
        except Exception as e:
            self.notifications.add(Event(
                _('Failed to save file'), str(e), level=WARNING),
                show_balloon=False)

    def update_mnu_recents(self):
        """
        Updates the recent files menu
        """
        self._mnu_recents.update_actions()

    def update_mnu_view(self):
        """
        Updates the list of window show in the view menu.
        """
        self._ui.mnu_windows.clear()
        self.window_group = QtWidgets.QActionGroup(self._ui.mnu_windows)
        open_windows = self.app.get_open_windows()
        _logger().debug('updating mnu_view: %r', open_windows)
        for w in open_windows:
            a = self._ui.mnu_windows.addAction(w.windowTitle())
            assert isinstance(a, QtWidgets.QAction)
            a.setCheckable(True)
            a.setChecked(w == self)
            self.window_group.addAction(a)
            a.setData(w)
        self.window_group.triggered.connect(self._on_window_action_triggered)

    def update_title(self):
        """
        Update the window title based on the project name and the
        current editor:

            PROJ_NAME - [current file path]
        """
        tab = self.current_tab
        if tab:
            # prj mode
            root_path = self.current_project
            root = os.path.split(root_path)[1]
            fpath = tab.file.path
            self.setWindowTitle('%s - [%s]' % (root, fpath))
        else:
            root_path = self.current_project
            root = os.path.split(root_path)[1]
            self.setWindowTitle('%s' % (root))

    def restore_state(self, pth=None):
        """
        Restore the window state (geometry and state).

        If settings.restore_session is True, it restore open files.
        """
        ret_val = False
        if pth is None:
            pth = self.projects[0]
        key = '%s_' % pth.replace('\\', '_').replace('/', '_')
        geometry = QtCore.QSettings().value('_window/geometry_' + key)
        if geometry:
            ret_val = True
            self.setGeometry(geometry)
        _logger().debug('restoreGeometry: OK')

        self.restoreState(QtCore.QSettings().value(
            '_window/state_' + key, b''))
        _logger().debug('restoreState: OK')

        if not self._ui.menuTools.actions():
            self._ui.menubar.removeAction(self._ui.menuTools.menuAction())

        self._files_to_restore = QtCore.QSettings().value(
            '_session/files_' + key, [])
        self._restore_index = int(QtCore.QSettings().value(
            '_session/index_' + key, 0))
        QtWidgets.qApp.processEvents()
        if settings.restore_session():
            _logger().debug('restoring session')
            while self._files_to_restore:
                _logger().debug('restoring file')
                self._restore_file()
                _logger().debug('file restored')
                QtWidgets.qApp.processEvents()
        if self.notifications.has_errors() or \
                self.notifications.has_warnings():
            self.notifications.show()

        self.state_restored.emit()
        QtWidgets.qApp.processEvents()

        return ret_val

    def apply_preferences(self):
        """
        Applies the preferences stored in QSettings.

        This method will apply preferences on each editor and on each
        plugin.
        """
        self.project_explorer.apply_preferences()
        self._dock_manager.update_style()
        self._apply_shortcuts()
        for toolbar in self._toolbars:
            s = settings.toolbar_icon_size()
            toolbar.setIconSize(QtCore.QSize(s, s))
        for editor in self.tab_widget.widgets():
            try:
                self._apply_editor_preferences(editor)
            except AttributeError:
                # not a CodeEdit
                _logger().debug('failed to apply preferences on editor %r',
                                editor)
        for plugin in self.plugins:
            plugin.apply_preferences()
        if settings.widescreen_layout():
            self.setCorner(
                QtCore.Qt.TopLeftCorner, QtCore.Qt.LeftDockWidgetArea)
            self.setCorner(
                QtCore.Qt.TopRightCorner, QtCore.Qt.RightDockWidgetArea)
            self.setCorner(
                QtCore.Qt.BottomLeftCorner, QtCore.Qt.LeftDockWidgetArea)
            self.setCorner(
                QtCore.Qt.BottomRightCorner, QtCore.Qt.RightDockWidgetArea)
        else:
            self.setCorner(
                QtCore.Qt.TopLeftCorner, QtCore.Qt.LeftDockWidgetArea)
            self.setCorner(
                QtCore.Qt.TopRightCorner, QtCore.Qt.RightDockWidgetArea)
            self.setCorner(
                QtCore.Qt.BottomLeftCorner, QtCore.Qt.BottomDockWidgetArea)
            self.setCorner(
                QtCore.Qt.BottomRightCorner, QtCore.Qt.BottomDockWidgetArea)

    # -------------------------------------------------------------------------
    # Private API (+ overridden methods)
    # -------------------------------------------------------------------------
    @staticmethod
    def dragEnterEvent(event):
        mime = event.mimeData()
        if mime is None or not mime.hasUrls():
            return
        event.accept()

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime is None or not mime.hasUrls():
            return
        for url in mime.urls():
            path = url.path()
            if system.WINDOWS and path.startswith('/'):
                path = path[1:]
            if os.path.isfile(path):
                # open a new editor
                self.open_file(path)
            else:
                # open a new window
                self.app.open_path(path)

    @staticmethod
    def createPopupMenu():
        # prevent the window to create its standard popup. That menu
        # is already visible in View->Tools menu.
        return None

    def addDockWidget(self, area, dock, orientation=None, special=False):
        self._dock_manager.add_dock_widget(dock, area, special)
        if orientation:
            super().addDockWidget(area, dock, orientation)
        else:
            super().addDockWidget(area, dock)
        self._dock_widgets.append(dock)

    def removeDockWidget(self, dock):
        if dock is None:
            return
        super().removeDockWidget(dock)
        self._dock_manager.remove_dock_widget(dock)
        self._dock_widgets.remove(dock)

    def addToolBar(self, *args):
        for arg in args:
            if isinstance(arg, QtWidgets.QToolBar):
                size = settings.toolbar_icon_size()
                arg.setIconSize(QtCore.QSize(size, size))
                self._toolbars.append(arg)
                break
        super().addToolBar(*args)

    def closeEvent(self, event):
        if self._ui:
            _logger().debug('close event')
            if self.app.window_count == 1 and settings.confirm_app_exit():
                answer = QtWidgets.QMessageBox.question(
                    self, _('Confirm exit'),
                    _('Are you sure you want to exit HackEdit?'),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes)
                if answer == QtWidgets.QMessageBox.No:
                    event.ignore()
                    return
            current_index, files = self.get_session_info()
            self.save_state(current_index, files)
            accept = self._close_documents(event)
            event.setAccepted(accept)
            if event.isAccepted():
                for plugin in self.plugins:
                    try:
                        plugin.close()
                    except AttributeError:
                        _logger().debug('plugin %r has not attribute close',
                                        plugin)
                    finally:
                        plugin.window = None
                self.plugins.clear()
                self.closed.emit(self)
                self._ui = None
                self.task_manager.terminate()
                self.notifications.close()
                self.notifications = None
                self.task_manager_widget.close()
                self._dock_manager.window = None
                self.project_explorer.close()

                if self.app.last_window == self:
                    self.app.last_window = None
                self.app = None

                self.setParent(None)

    def event(self, e):
        if e.type() == QtCore.QEvent.WindowActivate and self.app:
            self.app.active_window = self
        return super().event(e)

    def showEvent(self, ev):
        super().showEvent(ev)
        if self.task_manager.count:
            self.task_manager_widget.show()

    @staticmethod
    def _setup_dark_editor(editor):
        try:
            panel = editor.panels.get('FoldingPanel')
        except KeyError:
            _logger().debug('no FoldingPanel on widget %r', editor)
        else:
            if settings.dark_theme():
                panel.native_look = False
        try:
            mode = editor.modes.get('OccurrencesHighlighterMode')
        except KeyError:
            _logger().debug('no OccurrencesHighlighterMode on widget %r',
                            editor)
        else:
            mode.background = QtGui.QColor('#344134')
            mode.foregound = None
        try:
            mode = editor.modes.get('SymbolMatcherMode')
        except KeyError:
            _logger().debug('no SymbolMatcherMode on widget %r', editor)
        else:
            mode.match_background = QtGui.QColor('#344134')
            mode.match_foreground = QtGui.QColor('yellow')

    @staticmethod
    def _setup_native_editor(editor):
        try:
            panel = editor.panels.get('FoldingPanel')
        except KeyError:
            _logger().debug('no FoldingPanel on widget %r', editor)
        else:
            panel.native_look = True
        try:
            mode = editor.modes.get('OccurrencesHighlighterMode')
        except KeyError:
            _logger().debug('no OccurrencesHighlighterMode on widget %r',
                            editor)
        else:
            mode.background = QtGui.QColor('#CCFFCC')
            mode.foregound = None
        try:
            mode = editor.modes.get('SymbolMatcherMode')
        except KeyError:
            _logger().debug('no SymbolMatcherMode on widget %r', editor)
        else:
            mode.match_background = QtGui.QColor('#CCFFCC')
            mode.match_foreground = QtGui.QColor('red')

    def get_session_info(self):
        widgets = self._ui.tabs.widgets()
        files = []
        current_index = 0
        for i, w in enumerate(widgets):
            try:
                # widget that have this attribute set won't be restored when
                # restoring session
                w.dont_remember
            except AttributeError:
                try:
                    path = w.file.path
                except AttributeError:
                    _logger().debug('widget %r has not attribute file.path', w)
                else:
                    files.append(path)
                    if path == self._ui.tabs.current_widget().file.path:
                        current_index = i
            else:
                continue
        return current_index, files

    def _close_documents(self, event=None):
        if event is None:
            event = QtGui.QCloseEvent()
            event.setAccepted(True)
        self._ui.tabs.closeEvent(event)
        accept = event.isAccepted()
        for dock in self._dock_widgets:
            dock.widget().closeEvent(event)
            if not event.isAccepted():
                accept = False
        return accept

    def save_state(self, current_index, files):
        if self._docks_to_restore:
            self._restore_children()
        pth = self.projects[0]
        key = '%s_' % pth.replace('\\', '_').replace('/', '_')
        QtCore.QSettings().setValue('_session/files_' + key, files)
        QtCore.QSettings().setValue('_session/index_' + key, int(current_index))
        QtCore.QSettings().setValue('_window/state_' + key, self.saveState())
        QtCore.QSettings().setValue('_window/geometry_' + key, self.geometry())

    def _restore_file(self):
        path = self._files_to_restore.pop(0)
        self.open_file(path)
        self._ui.tabs.main_tab_widget.setCurrentIndex(self._restore_index)

    def _setup_status_bar_widgets(self):
        if psutil:
            self.lbl_memory = QtWidgets.QLabel()
            self.lbl_memory.setText('0 MiB')

        self.lbl_cursor = ClickableLabel()
        self.lbl_cursor.setText('1:1', False)
        self.lbl_cursor.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.lbl_cursor.clicked.connect(self._on_label_cursor_clicked)

        self.lbl_encoding = ClickableLabel()
        self.lbl_encoding.setText(_('n/a'), False)
        self.lbl_encoding.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.lbl_encoding.clicked.connect(self._on_label_encodings_clicked)

    def setup_status_bar(self):
        self.add_statusbar_widget(self.lbl_cursor)
        self.add_statusbar_widget(self.lbl_encoding)
        if psutil:
            self.add_statusbar_widget(self.lbl_memory)

    def _connect_slots(self):
        self._ui.tabs.editor_created.connect(self.editor_created.emit)
        self._ui.tabs.document_opened.connect(self.editor_loaded.emit)
        self._ui.tabs.document_saved.connect(self.document_saved.emit)
        self._ui.tabs.editor_created.connect(self._apply_editor_preferences)
        self._ui.action_new.triggered.connect(self._on_new_triggered)
        self._ui.action_help.triggered.connect(self._show_not_implemented_msg)
        self._ui.action_check_for_update.triggered.connect(
            self._show_not_implemented_msg)
        self._ui.tabs.current_changed.connect(self.on_current_tab_changed)
        self._ui.action_close.triggered.connect(self.close)
        self._ui.action_quit.triggered.connect(QtWidgets.qApp.closeAllWindows)
        self._ui.action_save.triggered.connect(self.save_current)
        self._ui.action_save_as.triggered.connect(self.save_current_as)
        self._ui.action_save_all.triggered.connect(self.save_all)
        self._ui.tabs.last_tab_closed.connect(self._on_last_tab_closed)
        self._ui.action_report_bug.triggered.connect(self._report_bug)
        self._ui.action_about.triggered.connect(self._show_about)
        self._ui.action_check_for_update.triggered.connect(
            self._check_for_update)
        self._ui.action_preferences.triggered.connect(self._edit_preferences)
        self._mnu_recents.open_requested.connect(
            self._on_open_recent_requested)
        self._ui.tabs.tab_detached.connect(self._on_tab_detached)
        self._ui.tabs.tab_detached.connect(self.editor_detached.emit)
        self._ui.a_print.triggered.connect(self._print)

    def _show_not_implemented_msg(self):
        common.not_implemented_action(self)

    def _on_label_cursor_clicked(self):
        if self.current_tab:
            self.project_explorer.action_goto_line.triggered.emit()

    def _on_label_encodings_clicked(self):
        if self.current_tab:
            mnu = EncodingsContextMenu(parent=self.current_tab)
            self.current_tab.remove_menu(mnu)
            mnu.reload_requested.connect(self._update_encoding_label)
            mnu.exec_(self.lbl_encoding.mapToGlobal(QtCore.QPoint(0, 0)))

    def _update_encoding_label(self, encoding):
        from pyqode.core.api import ENCODINGS_MAP
        try:
            self.lbl_encoding.setText(ENCODINGS_MAP[encoding][0], False)
        except KeyError:
            self.lbl_encoding.setText(encoding, False)

    def _setup_actions(self):
        self._ui.action_about.setMenuRole(QtWidgets.QAction.AboutRole)
        self._ui.action_preferences.setMenuRole(
            QtWidgets.QAction.PreferencesRole)
        self._ui.action_quit.setMenuRole(QtWidgets.QAction.QuitRole)
        self._ui.action_check_for_update.setMenuRole(
            QtWidgets.QAction.ApplicationSpecificRole)

    def _get_linked_paths(self):
        data = load_user_config(self.projects[0])
        try:
            linked_paths = data['linked_paths']
        except KeyError:
            return []
        else:
            ret_val = []
            for p in linked_paths:
                if os.path.exists(p):
                    ret_val.append(p)
            return ret_val

    def _save_linked_paths(self, linked_paths):
        data = load_user_config(self.projects[0])
        data['linked_paths'] = linked_paths
        try:
            save_user_config(self.projects[0], data)
        except PermissionError:
            _logger().warn('failed to save linked paths, permission error')

    def _on_window_action_triggered(self, action):
        _logger().debug('window action triggered')
        self.app.active_window = action.data()

    def _on_last_tab_closed(self):
        _logger().debug('last tab closed')
        self.on_current_tab_changed(None)

    def _on_open_recent_requested(self, path):
        _logger().debug('open recent requested')
        self.app.open_path(path, sender=self)

    # Private slots
    def _on_new_triggered(self):
        common.create_new(self.app, self, self.current_project)

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    def on_current_tab_changed(self, tab):
        self._current_tab = tab
        _logger().debug('current tab changed: %r', tab)
        self.current_tab_changed.emit(tab)
        if tab:
            self._ui.menuActive_editor.clear()
            self._ui.menuActive_editor.addActions(
                [a for a in tab.actions() if not hasattr(
                    a, 'dont_show_in_edit_menu')])
            self._ui.menuActive_editor.addSeparator()
            try:
                for m in tab.menus():
                    self._ui.menuActive_editor.addMenu(m)
            except AttributeError:
                # not a code edit
                _logger().debug('failed to add editor menus to Edit -> Active '
                                'editor, not a CodeEdit instance')
            self._ui.stackedWidget.setCurrentIndex(PAGE_EDITOR)
            try:
                self._update_cursor_label()
                tab.cursorPositionChanged.connect(
                    self._update_cursor_label, QtCore.Qt.UniqueConnection)
            except TypeError:
                # already connected
                _logger().debug('failed to connect to cursorPositionChanged '
                                'signal, already connected')
            except AttributeError:
                # not a code editor widget
                self.lbl_cursor.setText('n/a', False)
            try:
                self._update_encoding_label(tab.file.encoding)
            except AttributeError:
                self.lbl_encoding.setText('n/a', False)
        else:
            if self._ui:
                self._ui.menuActive_editor.clear()
                self._ui.stackedWidget.setCurrentIndex(PAGE_EXPLANATIONS)
                try:
                    self.lbl_encoding.setText('n/a', False)
                    self.lbl_cursor.setText('n/a', False)
                except AttributeError:
                    _logger().debug('failed to reset cursor infos labels, '
                                    'widget deleted (window is closing...)')

    @QtCore.pyqtSlot()
    def on_action_open_triggered(self):
        """ Opens a project directory"""
        common.open_folder(self, self.app)

    @QtCore.pyqtSlot()
    def on_action_open_file_triggered(self):
        """
        Opens a file.
        """
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Open file'), settings.last_open_dir())
        if path:
            settings.set_last_open_dir(os.path.dirname(path))
            self.open_file(path)

    @QtCore.pyqtSlot()
    def on_a_fullscreen_triggered(self):
        state = self._ui.a_fullscreen.isChecked()
        if state:
            self.showFullScreen()
        else:
            self.showNormal()

    @QtCore.pyqtSlot()
    def on_a_menu_triggered(self):
        state = self._ui.a_menu.isChecked()
        settings.set_show_menu(state)
        self._update_menu_visibility()

    @QtCore.pyqtSlot()
    def _report_bug(self):
        common.report_bug(self)

    @QtCore.pyqtSlot()
    def _show_about(self):
        common.show_about(self)

    @QtCore.pyqtSlot()
    def _check_for_update(self):
        common.check_for_update(self)

    def _restore_children(self):
        for dock in self._docks_to_restore:
            dock.show()
        self._docks_to_restore[:] = []
        for tb in self._toolbars:
            if self.toolBarArea(tb) == QtCore.Qt.TopToolBarArea:
                tb.show()

    def _hide_children(self):
        for dock in self._dock_manager.dock_widgets():
            if dock.isVisible():
                self._docks_to_restore.append(dock)
                dock.hide()
        for tb in self._toolbars:
            if self.toolBarArea(tb) == QtCore.Qt.TopToolBarArea:
                tb.hide()

    def _edit_preferences(self):
        DlgPreferences.edit_preferences(self, self.app)

    def _apply_editor_plugin_preferences(self, editor):
        for plugin in self.app.plugin_manager.editor_plugins:
            if plugin.get_editor_class() == editor.__class__:
                try:
                    plugin.apply_specific_preferences(editor)
                except Exception:
                    _logger().exception('failed to apply specific preferences')
                finally:
                    break

    def _apply_shortcuts(self):
        # File
        self._ui.action_new.setShortcut(shortcuts.get(
            'New', _('New'), 'Ctrl+N'))
        self._ui.action_open.setShortcut(shortcuts.get(
            'Open directory', _('Open directory'), 'Ctrl+O'))
        self._ui.action_save.setShortcut(shortcuts.get(
            'Save', _('Save'), 'Ctrl+S'))
        self._ui.action_save_as.setShortcut(shortcuts.get(
            'Save as', _('Save as'), 'Ctrl+Shift+S'))
        self._ui.action_save_all.setShortcut(shortcuts.get(
            'Save all', _('Save all'), 'Ctrl+Alt+S'))
        self._ui.action_open_file.setShortcut(shortcuts.get(
            'Open file', _('Open file'), 'Ctrl+Shift+O'))
        self._ui.action_close.setShortcut(shortcuts.get(
            'Close window', _('Close window'), 'Ctrl+Shift+Q'))
        self._ui.action_quit.setShortcut(shortcuts.get(
            'Quit', _('Quit'), 'Ctrl+Q'))
        # Edit
        self._ui.action_preferences.setShortcut(shortcuts.get(
            'Preferences', _('Preferences'), 'Ctrl+,'))

        for editor in self.tab_widget.widgets(True):
            if not isinstance(editor, CodeEdit):
                continue
            self._apply_editor_shortcuts(editor)

        # View
        self._ui.a_fullscreen.setShortcut(shortcuts.get(
            'Toggle fullscreen', _('Toggle fullscreen'), 'Ctrl+F11'))
        self._ui.a_menu.setShortcut(shortcuts.get(
            'Toggle menu', _('Toggle menu'), 'Ctrl+M'))

    @staticmethod
    def _apply_editor_shortcuts(editor):
        editor.action_undo.setShortcut(shortcuts.get(
            'Undo', _('Undo'), 'Ctrl+Z'))
        editor.action_redo.setShortcut(shortcuts.get(
            'Redo', _('Redo'), 'Ctrl+Y'))
        editor.action_copy.setShortcut(shortcuts.get(
            'Copy', _('Copy'), 'Ctrl+C'))
        editor.action_cut.setShortcut(shortcuts.get(
            'Cut', _('Cut'), 'Ctrl+X'))
        editor.action_paste.setShortcut(shortcuts.get(
            'Paste', _('Paste'), 'Ctrl+V'))
        editor.action_duplicate_line.setShortcut(shortcuts.get(
            'Duplicate line', _('Duplicate line'), 'Ctrl+D'))
        editor.action_goto_line.setShortcut(shortcuts.get(
            'Goto line', _('Goto line'), 'Ctrl+G'))
        try:
            p = editor.panels.get('SearchAndReplacePanel')
        except KeyError:
            _logger().debug('no SearchAndReplacePanel on widget %r', editor)
        else:
            p.actionSearch.setShortcut(shortcuts.get(
                'Find', _('Find'), 'Ctrl+F'))
            p.actionActionSearchAndReplace.setShortcut(
                shortcuts.get('Replace', _('Replace'), 'Ctrl+H'))
            p.actionFindNext.setShortcut(shortcuts.get(
                'Find next', _('Find next'), 'F3'))
            p.actionFindPrevious.setShortcut(shortcuts.get(
                'Find previous', _('Find previous'), 'Shift+F3'))
        try:
            p = editor.panels.get('FoldingPanel')
        except KeyError:
            _logger().debug('no FoldingPanel on widget %r', editor)
        else:
            p.action_collapse.setShortcut(shortcuts.get(
                'Folding: collapse', _('Folding: collapse'), 'Shift+-'))
            p.action_expand.setShortcut(shortcuts.get(
                'Folding: expand', _('Folding: expand'), 'Shift++'))
            p.action_collapse_all.setShortcut(shortcuts.get(
                'Folding: collapse all', _('Folding: collapse all'),
                'Ctrl+Shift+-'))
            p.action_expand_all.setShortcut(shortcuts.get(
                'Folding: expand all', _('Folding: expand all'),
                'Ctrl+Shift++'))

        try:
            m = editor.modes.get('ExtendedSelectionMode')
        except KeyError:
            _logger().debug('no ExtendedSelectionMode on widget %r', editor)
        else:
            m.action_select_word.setShortcut(shortcuts.get(
                'Select word', _('Select word'), 'Ctrl+Alt+J'))
            m.action_select_extended_word.setShortcut(shortcuts.get(
                'Select extended word', _('Select extended word'),
                'Ctrl+Shift+J'))
            m.action_select_matched.setShortcut(shortcuts.get(
                'Matched select', _('Matched select'), 'Ctrl+E'))
            m.action_select_line.setShortcut(shortcuts.get(
                'Select line', _('Select line'), 'Ctrl+Shift+L'))

        try:
            m = editor.modes.get('CaseConverterMode')
        except KeyError:
            _logger().debug('no CaseConverterMode on widget %r', editor)
        else:
            m.action_to_lower.setShortcut(shortcuts.get(
                'Convert to lower case', _('Convert to lower case'), 'Ctrl+U'))
            m.action_to_upper.setShortcut(shortcuts.get(
                'Convert to UPPER CASE', _('Convert to UPPER CASE'),
                'Ctrl+Shift+U'))

    def _on_tab_detached(self, _, tab):
        self._apply_editor_preferences(tab)

    def _print(self):
        printer = QtPrintSupport.QPrinter()
        try:
            document = self.current_tab.document()
            has_selection = self.current_tab.textCursor().hasSelection()
        except AttributeError:
            # not a code editor
            return
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        dialog.setOption(dialog.PrintSelection, has_selection)
        dialog.setWindowTitle(_('Print current editor'))
        if dialog.exec_() == dialog.Accepted:
            document.print(printer)

    def _apply_editor_preferences(self, editor, set_color_scheme=True):
        if not isinstance(editor, CodeEdit):
            return
        editor.show_whitespaces = settings.show_whitespaces()
        if set_color_scheme:
            editor.syntax_highlighter.color_scheme = ColorScheme(
                settings.color_scheme())
        editor.font_size = settings.editor_font_size()
        editor.font_name = settings.editor_font()
        if settings.dark_theme() or settings.is_dark_color_scheme():
            self._setup_dark_editor(editor)
        else:
            self._setup_native_editor(editor)
        editor.tab_length = settings.tab_length()
        editor.use_spaces_instead_of_tabs = \
            settings.use_spaces_instead_of_tabs()
        editor.setCenterOnScroll(settings.center_on_scroll())
        editor.file.replace_tabs_by_spaces = settings.convert_tabs()
        editor.file.safe_save = settings.safe_save()
        editor.file.clean_trailing_whitespaces = \
            settings.clean_trailing_whitespaces()
        editor.file.restore_cursor = settings.restore_cursor()
        editor.file.preferred_eol = settings.eol_convention()
        editor.file.autodetect_eol = settings.autodetect_eol()
        editor.setLineWrapMode(
            editor.WidgetWidth if settings.text_wrapping() else
            editor.NoWrap)
        try:
            mode = editor.modes.get(modes.RightMarginMode)
        except KeyError:
            _logger().debug('no RightMarginMode on widget %r', editor)
        else:
            if 'cobol' not in editor.__class__.__name__.lower():
                mode.position = settings.margin_position()
                mode.enabled = settings.right_margin()

        try:
            mode = editor.modes.get(modes.CodeCompletionMode)
        except KeyError:
            _logger().debug('no CodeCompletionMode on widget %r', editor)
        else:
            mode.filter_mode = settings.cc_filter_mode()
            mode.trigger_length = settings.cc_trigger_len()
            mode.case_sensitive = settings.cc_case_sensitive()
            mode.show_tooltips = settings.cc_show_tooltips()

        try:
            mode = editor.modes.get(modes.CaretLineHighlighterMode)
        except KeyError:
            _logger().debug('no CaretLineHighlighterMode on widget %r', editor)
        else:
            mode.enabled = settings.highlight_caret_line()

        try:
            mode = editor.modes.get(modes.SymbolMatcherMode)
        except KeyError:
            _logger().debug('no SymbolMatcherMode on widget %r', editor)
        else:
            mode.enabled = settings.highlight_parentheses()

        try:
            mode = editor.modes.get(modes.SmartBackSpaceMode)
        except KeyError:
            _logger().debug('no SmartBackSpaceMode on widget %r', editor)
        else:
            mode.enabled = settings.backspace_unindents()

        # those modes are typically subclasses
        available_modes = editor.modes.keys()
        for name in available_modes:
            if 'autocomplete' in name.lower():
                mode = editor.modes.get(name)
                mode.enabled = settings.auto_complete()
                break
        for name in available_modes:
            if 'autoindent' in name.lower():
                mode = editor.modes.get(name)
                mode.enabled = settings.auto_indent()
                break
        try:
            panel = editor.panels.get(panels.LineNumberPanel)
        except KeyError:
            _logger().debug('no LineNumberPanel on widget %r', editor)
        else:
            panel.setVisible(settings.show_line_numbers_panel())

        try:
            panel = editor.panels.get(panels.CheckerPanel)
        except KeyError:
            _logger().debug('no CheckerPanel on widget %r', editor)
        else:
            panel.setVisible(settings.show_errors_panel())

        try:
            panel = editor.panels.get(panels.GlobalCheckerPanel)
        except KeyError:
            _logger().debug('no GlobalCheckerPanel on widget %r', editor)
        else:
            panel.setVisible(settings.show_global_panel())

        try:
            panel = editor.panels.get(panels.FoldingPanel)
        except KeyError:
            _logger().debug('no FoldingPanel on widget %r', editor)
        else:
            panel.highlight_caret_scope = settings.highlight_caret_scope()
            panel.setVisible(settings.show_folding_panel())

        self._apply_editor_shortcuts(editor)
        self._apply_editor_plugin_preferences(editor)

    def _update_cursor_label(self):
        try:
            l, c = TextHelper(self.current_tab).cursor_position()
            self.lbl_cursor.setText('%d:%d' % (l+1, c+1), False)
        except (AttributeError, TypeError):
            try:
                l, c = self.current_tab.cursor_position
                self.lbl_cursor.setText('%d:%d' % (l+1, c+1), False)
            except AttributeError:
                self.lbl_cursor.setText('n/a', False)

    def _update_mem_label(self):
        if psutil:
            process = psutil.Process(os.getpid())
            mem = int(process.memory_info().rss) / 1024 / 1024
            self.lbl_memory.setText('%.3f MiB' % mem)
            self._update_mem_label_timer.start()

    def _update_menu_visibility(self):
        self.ui.a_menu.setChecked(settings.show_menu())
        self.ui.menubar.setVisible(settings.show_menu())
        self.toolbar_menu.setVisible(not settings.show_menu())

    def _update_menu_button(self):
        for a in self.menu_button.actions():
            self.menu_button.removeAction(a)
        for menu in self._menus_list:
            self.menu_button.addAction(menu.menuAction())
