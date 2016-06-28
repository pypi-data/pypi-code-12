"""
This plugin show the project contents in a tree view.
"""
import pkg_resources
import logging
import mimetypes
import os
import shlex
import subprocess
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqode.core.api import DelayJobRunner, TextHelper
from pyqode.core.widgets import FileSystemTreeView, FileSystemContextMenu, \
    FileSystemHelper

from hackedit import api
from hackedit.api import shortcuts, utils, index
from hackedit.api.project import load_user_config, save_user_config
from hackedit.api.widgets import FileIconProvider
from hackedit.app import settings, templates, common
from hackedit.app.dialogs.dlg_ignore import DlgIgnore
from hackedit.app.index.db import DbHelper
from hackedit.app.index.backend import index_project_files, update_file, get_symbol_parser, rename_files, delete_files
from hackedit.app.widgets.locator import LocatorWidget
from hackedit.app.workspaces import WorkspaceManager


def _logger():
    return logging.getLogger(__name__)


class ProjectIndexor:
    """
    Utility class to perform project indexation.
    """
    def __init__(self, project, window):
        self.project = project
        self.main_window = window
        self._running_task = None
        self.perform_indexing()

    def cancel(self):
        if self._running_task:
            self._running_task.cancel()
        self._running_task = None

    def perform_indexing(self):
        if self._running_task is None:
            _logger().info('indexing project %r', self.project)
            self._running_task = index.perform_indexation(
                [self.project], callback=self._on_finished,
                task_name=_('Indexing project: %s' % os.path.split(
                    self.project)[1]))

    def _on_finished(self, *args):
        _logger().info('finished indexing of project %r', self.project)
        self._running_task = None


class ProjectExplorer(QtCore.QObject):
    """
    Displays project content in a treeview, manage the list of open projects
    and provides the list of project files to other plugins.

    This is a central plugin that all workspace should include!
    """
    project_only = True
    preferred_position = 0

    def __init__(self, window):
        super().__init__()
        self.main_window = window
        self.parser_plugins = []
        self._indexors = []
        self._locator = LocatorWidget(self.main_window)
        self._locator.activated.connect(self._on_locator_activated)
        self._locator.cancelled.connect(self._on_locator_cancelled)
        self._widget = QtWidgets.QWidget(self.main_window)
        self._job_runner = DelayJobRunner()
        self._cached_files = []
        self._running_tasks = False
        self._widget.installEventFilter(self)
        self._setup_filesystem_treeview()
        self._setup_prj_selector_widget(self.main_window)
        self._setup_dock_widget()
        self._setup_tab_bar_context_menu(self.main_window)
        self._setup_locator()
        self._setup_project_menu()
        self._load_parser_plugins()
        api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED,
                                 self._on_current_editor_changed)

    def activate(self):
        for p in api.project.get_projects():
            self._indexors.append(ProjectIndexor(p, self.main_window))

    def _load_parser_plugins(self):
        _logger().debug('loading symbol parser plugins')
        for entrypoint in pkg_resources.iter_entry_points(
                api.plugins.SymbolParserPlugin.ENTRYPOINT):
            _logger().debug('  - loading plugin: %s', entrypoint)
            try:
                plugin = entrypoint.load()()
            except ImportError:
                _logger().exception('failed to load plugin')
            else:
                self.parser_plugins.append(plugin)
                _logger().debug('  - plugin loaded: %s', entrypoint)
        _logger().debug('indexor plugins: %r', self.parser_plugins)

    @staticmethod
    def get_ignored_patterns():
        patterns = utils.get_ignored_patterns()
        prj_path = api.project.get_root_project()
        # project specific ignore patterns
        usd = api.project.load_user_config(prj_path)
        try:
            patterns += usd['ignored_patterns']
        except KeyError:
            _logger().debug('no ignored patterns found in user config')
        return patterns

    def _run_update_projects_model_thread(self):
        if not self._running_tasks:
            self._running_tasks += 1
            for project_dir in api.project.get_projects():
                db_path = os.path.join(project_dir, '.hackedit', 'project.db')
                api.tasks.start(
                    _('Indexing project files (%r)') % os.path.split(
                        project_dir)[1],
                    index_project_files,
                    self._on_file_list_available,
                    args=(db_path, project_dir, self.get_ignored_patterns(),
                          self.parser_plugins), cancellable=True)

    def close(self):
        # save active project in first open project
        paths = api.project.get_projects()
        data = load_user_config(paths[0])
        data['active_project'] = self._combo_projects.currentData()
        try:
            save_user_config(paths[0], data)
        except PermissionError:
            _logger().warn('failed to save user config to %r, '
                           'permission error', paths[0])
        self.main_window = None
        self._locator.window = None
        self._locator = None

    def apply_preferences(self):
        new_patterns = ';'.join(utils.get_ignored_patterns())
        if self._last_ignore_patterns != new_patterns:
            self._last_ignore_patterns = new_patterns
            self.view.clear_ignore_patterns()
            self.view.add_ignore_patterns(self.get_ignored_patterns())
            self.view.set_root_path(api.project.get_current_project())
        self.view.context_menu.update_show_in_explorer_action()
        self._tab_bar_action_show_in_explorer.setText(
            _('Show in %s') % FileSystemContextMenu.get_file_explorer_name())
        self._update_workspaces_menu()
        self.action_goto_anything.setShortcut(shortcuts.get(
            'Goto anything', _('Goto anything'), 'Ctrl+P'))
        self.action_goto_symbol.setShortcut(shortcuts.get(
            'Goto symbol', _('Goto symbol'), 'Ctrl+R'))
        self.action_goto_symbol_in_project.setShortcut(shortcuts.get(
            'Goto symbol in project', _('Goto symbol in project'),
            'Ctrl+Shift+R'))
        self.action_goto_line.setShortcut(shortcuts.get(
            'Goto line', _('Goto line'), 'Ctrl+G'))
        self._update_templates_menu()
        menu = api.window.get_menu(_('&Goto'))
        for action in menu.actions():
            action.setEnabled(settings.indexing_enabled())
        tab = api.editor.get_current_editor()
        self.action_goto_line.setEnabled(tab is not None)
        if self.main_window.app.flg_force_indexing:
            self._reindex_all_projects()
        if not settings.indexing_enabled():
            for indexor in self._indexors:
                indexor.cancel()

    def _on_file_list_available(self, status):
        self._running_tasks = False
        if status is False:
            # too much file indexed, display a warning to let the user know
            # he should ignore some unwanted directories.
            event = api.events.Event(
                _('Project directory contains too much files for indexing...'),
                _('You might want to mark the directories that contains '
                  'non-project files as ignored (<i>Project View -> Right '
                  'click on a directory -> Mark as ignored</i>)'),
                level=api.events.WARNING)
            api.events.post(event)
        self.main_window.project_files_available.emit()
        _logger().debug('project model updated')

    def _setup_tab_bar_context_menu(self, window):
        text = _('Show in %s') % FileSystemContextMenu.get_file_explorer_name()
        action = QtWidgets.QAction(text, window)
        action.setToolTip(text)
        action.setIcon(QtGui.QIcon.fromTheme('system-file-manager'))
        action.triggered.connect(self._on_show_in_explorer_triggered)
        api.window.add_tab_widget_context_menu_action(action)
        self._tab_bar_action_show_in_explorer = action

    def _setup_dock_widget(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._widget_active_projects)
        layout.addWidget(self.view)
        layout.setContentsMargins(3, 3, 3, 3)
        self._widget.setLayout(layout)
        dock = api.window.add_dock_widget(
            self._widget, _('Project'), QtGui.QIcon.fromTheme('folder'),
            QtCore.Qt.LeftDockWidgetArea)
        dock.show()

    def _setup_project_menu(self):
        menu = api.window.get_menu(_('&View'))
        self.workspaces_menu = menu.addMenu(_('Workspaces'))
        menu.addSeparator()

    def _update_workspaces_menu(self):
        if QtGui.QIcon.hasThemeIcon('preferences-system-windows'):
            icon = QtGui.QIcon.fromTheme('preferences-system-windows')
        else:
            icon = QtGui.QIcon.fromTheme('applications-interfacedesign')
        self.workspaces_menu.clear()
        ag = QtWidgets.QActionGroup(self.workspaces_menu)
        for w in WorkspaceManager().get_names():
            a = QtWidgets.QAction(w, self.workspaces_menu)
            a.setCheckable(True)
            a.setChecked(w == self.main_window.workspace['name'])
            a.setIcon(icon)
            ag.addAction(a)
            self.workspaces_menu.addAction(a)
        ag.triggered.connect(self._on_workspace_action_clicked)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def _on_workspace_action_clicked(self, action):
        prj = api.project.get_root_project()
        open_path = self.main_window.app.open_path
        api.project.save_workspace(prj, action.text().replace('&', ''))
        self.main_window.save_state(*self.main_window.get_session_info())
        window = self.main_window
        open_path(prj, force=True)
        QtCore.QTimer.singleShot(1, window.close)

    def _setup_locator(self):
        menu = api.window.get_menu(_('&Goto'))
        self.action_goto_anything = menu.addAction(_('Goto anything...'))
        self.action_goto_anything.setShortcut(shortcuts.get(
            'Goto anything', _('Goto anything'), 'Ctrl+P'))
        self.main_window.addAction(self.action_goto_anything)
        self.action_goto_anything.triggered.connect(self._goto_anything)

        menu.addSeparator()

        self.action_goto_symbol = menu.addAction(_('Goto symbol...'))
        self.action_goto_symbol.setShortcut(shortcuts.get(
            'Goto symbol', _('Goto symbol'), 'Ctrl+R'))
        self.main_window.addAction(self.action_goto_symbol)
        self.action_goto_symbol.triggered.connect(self._goto_symbol)

        self.action_goto_symbol_in_project = menu.addAction(
            _('Goto symbol in project...'))
        self.action_goto_symbol_in_project.setShortcut(shortcuts.get(
            'Goto symbol in project', _('Goto symbol in project'),
            'Ctrl+Shift+R'))
        self.main_window.addAction(self.action_goto_symbol_in_project)
        self.action_goto_symbol_in_project.triggered.connect(
            self._goto_symbol_in_project)

        self.action_goto_line = menu.addAction(_('Goto line'))
        self.action_goto_line.setShortcut(shortcuts.get(
            'Goto line', _('Goto line'), 'Ctrl+G'))
        self.main_window.addAction(self.action_goto_line)
        self.action_goto_line.triggered.connect(self._goto_line)

        menu.addSeparator()

        indexing_menu = menu.addMenu('Indexing')
        action = indexing_menu.addAction('Update project(s) index')
        action.setToolTip('Update project index database...')
        action.triggered.connect(self._reindex_all_projects)
        action = indexing_menu.addAction('Force full project(s) indexation')
        action.setToolTip('Invalidate project index and force a full '
                          'reindexation...')
        action.triggered.connect(self._force_reindex_all_projects)

    def _goto_anything(self):
        self._locator.mode = self._locator.MODE_GOTO_ANYTHING
        self._show_locator()

    def _goto_symbol(self):
        try:
            self._cached_cursor_position = TextHelper(
                api.editor.get_current_editor()).cursor_position()
        except (TypeError, AttributeError):
            pass  # no current editor or not a code edit
        else:
            self._locator.mode = self._locator.MODE_GOTO_SYMBOL
            self._show_locator()

    def _goto_symbol_in_project(self):
        self._locator.mode = self._locator.MODE_GOTO_SYMBOL_IN_PROJECT
        self._show_locator()

    def _goto_line(self):
        self._cached_cursor_position = TextHelper(
            api.editor.get_current_editor()).cursor_position()
        self._locator.mode = self._locator.MODE_GOTO_LINE
        self._show_locator()

    def _show_locator(self):
        widget = api.window.get_main_window_ui().stackedWidget
        parent_pos = widget.pos()
        parent_size = widget.size()
        w = parent_size.width() * 0.8
        self._locator.setMinimumWidth(parent_size.width() * 0.8)
        x, y = parent_pos.x(), parent_pos.y()
        pw = parent_size.width()
        x += pw / 2 - w / 2
        self._locator.move(widget.mapToGlobal(QtCore.QPoint(x, y)))
        self._locator.show()

    def _setup_prj_selector_widget(self, window):
        self._widget_active_projects = QtWidgets.QWidget(window)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._combo_projects = QtWidgets.QComboBox()
        layout.addWidget(self._combo_projects)
        self.load_project_combo()
        api.signals.connect_slot(api.signals.PROJECT_ADDED,
                                 self._on_path_added)
        api.signals.connect_slot(api.signals.CURRENT_PROJECT_CHANGED,
                                 self._on_current_proj_changed)
        self._set_active_project()
        self._combo_projects.currentIndexChanged.connect(
            self._on_current_index_changed)
        bt_refresh = QtWidgets.QToolButton()
        bt_refresh.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        bt_refresh.setToolTip(
            _('Refresh project tree view...'))
        bt_refresh.clicked.connect(self._refresh)
        layout.addWidget(bt_refresh)

        bt_remove_project = QtWidgets.QToolButton()
        bt_remove_project.setIcon(QtGui.QIcon.fromTheme('list-remove'))
        bt_remove_project.setToolTip(
            _('Remove project from view'))
        bt_remove_project.clicked.connect(self._remove_current_project)
        layout.addWidget(bt_remove_project)
        self._widget_active_projects.setLayout(layout)
        self.bt_rm_proj = bt_remove_project
        if self._combo_projects.count() == 1:
            self.bt_rm_proj.hide()

    def load_project_combo(self, current_index=None):
        if current_index is None:
            current_index = self._combo_projects.currentIndex()
        project_paths = api.project.get_projects()
        with api.utils.block_signals(self._combo_projects):
            self._combo_projects.clear()
            for pth in project_paths:
                index = self._combo_projects.count()
                if os.path.ismount(pth):
                    if api.system.WINDOWS and not pth.endswith('\\'):
                        pth += '\\'
                    name = pth
                else:
                    name = os.path.split(pth)[1]
                self._combo_projects.addItem(name)
                self._combo_projects.setItemIcon(
                    index, FileIconProvider().icon(QtCore.QFileInfo(pth)))
                self._combo_projects.setItemData(index, pth)
        self._combo_projects.setCurrentIndex(current_index)

    def _setup_filesystem_treeview(self):
        self.view = FileSystemTreeView(self._widget)
        self.view.setMinimumWidth(200)
        self._last_ignore_patterns = ';'.join(utils.get_ignored_patterns())
        self.view.add_ignore_patterns(self.get_ignored_patterns())
        self.view.file_created.connect(self._on_file_created)
        self.view.files_deleted.connect(self._on_files_deleted)
        self.view.files_renamed.connect(self._on_files_renamed)
        self.main_window.document_saved.connect(self._on_file_saved)
        self.view.set_icon_provider(FileIconProvider())
        context_menu = FileSystemContextMenu()
        self.view.set_context_menu(context_menu)
        self.templates_menu = context_menu.menu_new.addSeparator()
        self.templates_menu = context_menu.menu_new.addMenu(
            _('Templates'))
        self.templates_menu.menuAction().setIcon(QtGui.QIcon.fromTheme(
            'folder-templates'))
        self._update_templates_menu()

        self.view.activated.connect(self._on_file_activated)

        self.action_mark_as_ignored = QtWidgets.QAction(
            _('Mark as ignored'), self.view)
        self.action_mark_as_ignored.triggered.connect(
            self._on_mark_as_ignored)
        self.action_mark_as_ignored.setIcon(QtGui.QIcon.fromTheme(
            'emblem-unreadable'))
        self.view.context_menu.insertAction(
            self.view.context_menu.action_show_in_explorer,
            self.action_mark_as_ignored)
        self.view.context_menu.insertSeparator(
            self.view.context_menu.action_show_in_explorer)

        self.action_show_in_terminal = QtWidgets.QAction(
            QtGui.QIcon.fromTheme('utilities-terminal'),
            _('Open in terminal'), self.view)
        self.action_show_in_terminal.triggered.connect(
            self._on_show_in_terminal_triggered)
        self.view.context_menu.addAction(self.action_show_in_terminal)

        self.action_open_in_browser = QtWidgets.QAction(
            QtGui.QIcon.fromTheme('applications-internet'),
            _('Open in web browser'), self.view)
        self.action_open_in_browser.triggered.connect(
            self._on_action_open_in_browser_triggered)
        self.view.context_menu.addAction(self.action_open_in_browser)

        insert_pt = self.view.context_menu.menu_new.menuAction()

        action = QtWidgets.QAction(_('Execute file'), self.main_window)
        action.setToolTip(_('Run executable'))
        action.setIcon(api.special_icons.run_icon())
        action.triggered.connect(self._execute_file)
        self.action_exec_file = action
        self.view.context_menu.insertAction(insert_pt, action)
        action = QtWidgets.QAction(self.main_window)
        action.setSeparator(True)
        self.view.context_menu.insertAction(insert_pt, action)

        self.view.about_to_show_context_menu.connect(
            self._on_about_to_show_context_menu)

    def _update_templates_menu(self):
        self.templates_menu.clear()
        sources = {}
        for src in templates.get_sources():
            lbl = src['label']
            icon = QtGui.QIcon.fromTheme('folder-templates')
            menu = self.templates_menu.addMenu(icon, lbl)
            sources[lbl] = menu
        for template in templates.get_templates(category='File'):
            icon = template['icon']
            lbl = template['source']['label']
            if icon.startswith(':') or os.path.exists(icon):
                icon = QtGui.QIcon(icon)
            elif icon.startswith('file.'):
                icon = FileIconProvider().icon(icon)
            else:
                icon = QtGui.QIcon.fromTheme(icon)
            a = sources[lbl].addAction(icon, template['name'])
            a.setData((lbl, template))
            a.triggered.connect(self._add_file_from_template)
        for menu in sources.values():
            menu.menuAction().setVisible(len(menu.actions()) > 0)

    def _on_mark_as_ignored(self):
        path = FileSystemHelper(self.view).get_current_path()
        prj = api.project.get_root_project()
        usd = api.project.load_user_config(prj)
        try:
            patterns = usd['ignored_patterns']
        except KeyError:
            patterns = []
        finally:
            name = os.path.split(path)[1]
            pattern = DlgIgnore.get_ignore_pattern(self.main_window, name)
            if pattern:
                patterns.append(pattern)
                usd['ignored_patterns'] = patterns
                api.project.save_user_config(prj, usd)
                self.view.clear_ignore_patterns()
                self.view.add_ignore_patterns(self.get_ignored_patterns())
                # force reload
                self.view.set_root_path(api.project.get_current_project())
                self._reindex_all_projects()

    def _on_about_to_show_context_menu(self, path):
        try:
            is_html = 'text/html' in mimetypes.guess_type(path)[0]
        except TypeError:
            is_html = False  # mimetype is None, not iterable
        self.action_open_in_browser.setVisible(is_html)
        if api.system.WINDOWS:
            is_executable = path.endswith('.exe') or path.endswith('.bat')
        else:
            is_executable = os.access(path, os.X_OK) and os.path.isfile(path)
        self.action_exec_file.setVisible(is_executable)

    def _on_action_open_in_browser_triggered(self):
        path = FileSystemHelper(self.view).get_current_path()
        if settings.use_default_browser():
            webbrowser.open_new_tab(path)
        else:
            cmd = utils.get_custom_browser_command() % path
            try:
                subprocess.Popen(cmd)
            except (OSError, subprocess.CalledProcessError):
                _logger().exception('failed to open file in browser (cmd=%s)',
                                    cmd)

    def _execute_file(self):
        path = FileSystemHelper(self.view).get_current_path()
        run_widget = api.window.get_run_widget()
        assert isinstance(run_widget, api.widgets.RunWidget)
        run_widget.run_program(path, cwd=os.path.dirname(path))

    def _on_show_in_terminal_triggered(self):
        path = FileSystemHelper(self.view).get_current_path()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        cmd = utils.get_cmd_open_folder_in_terminal() % path
        try:
            if api.system.WINDOWS:
                subprocess.Popen(
                    cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(shlex.split(cmd, posix=False))
        except (OSError, subprocess.CalledProcessError):
            _logger().exception('failed to open directory in terminal')

    def _add_file_from_template(self):
        source, template = self.sender().data()
        path = FileSystemHelper(self.view).get_current_path()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        path = common.create_new_from_template(
            source, template, path, True, self.main_window,
            self.main_window.app)
        self._on_file_created(path)

    @staticmethod
    def _on_show_in_explorer_triggered():
        path = api.window.get_tab_under_context_menu().file.path
        FileSystemContextMenu.show_in_explorer(
            path, api.window.get_main_window())

    def _on_file_activated(self, index):
        path = self.view.filePath(index)
        if path and os.path.isfile(path):
            _logger().debug('showing editor for %r', path)
            api.editor.open_file(path)

    def _on_current_editor_changed(self, tab):
        if tab is not None:
            self.view.select_path(tab.file.path)
        self.action_goto_line.setEnabled(tab is not None)
        self.action_goto_symbol.setEnabled(
            tab is not None and settings.indexing_enabled())

    def _on_current_proj_changed(self, new_path):
        if api.project.get_current_project() != new_path:
            self.main_window.current_project = new_path
            self.view.set_root_path(new_path)

    def _set_active_project(self):
        paths = api.project.get_projects()
        try:
            data = load_user_config(paths[0])
        except IndexError:
            return
        try:
            active_path = data['active_project']
            if active_path is None or not os.path.exists(active_path):
                raise KeyError('active_project')
        except KeyError:
            active_path = paths[0]
        for i in range(self._combo_projects.count()):
            if self._combo_projects.itemData(i) == active_path:
                self._combo_projects.setCurrentIndex(i)
                self.view.set_root_path(active_path)
                break
        else:
            self.view.set_root_path(active_path)
        self.main_window.current_project = active_path

    def _on_path_added(self, path):
        if os.path.isfile(path):
            return
        index = self._combo_projects.count()
        self.load_project_combo(current_index=index)
        self._on_current_index_changed(index)
        self.bt_rm_proj.setVisible(self._combo_projects.count() > 1)
        data = load_user_config(api.project.get_projects()[0])
        data['active_project'] = path
        self._indexors.append(ProjectIndexor(path, self.main_window))

    def _on_current_index_changed(self, index):
        new_path = self._combo_projects.itemData(index)
        if new_path:
            self.main_window.current_project_changed.emit(new_path)

    def _refresh(self):
        self.view.set_root_path('/')
        self.view.set_root_path(api.project.get_current_project())

    def _force_reindex_all_projects(self):
        for indexor in self._indexors:
            indexor.cancel()
        # wait a bit before removing the index database (to make sure
        # pending indexation tasks are actually canceled).
        QtCore.QTimer.singleShot(100, self._perform_full_reindexation)

    def _perform_full_reindexation(self):
        for project in api.project.get_projects():
            index.remove_project(project)
        self._reindex_all_projects()

    def _reindex_all_projects(self):
        for indexor in self._indexors:
            indexor.cancel()
        QtCore.QTimer.singleShot(100, self._perform_reindexation)

    def _perform_reindexation(self):
        for indexor in self._indexors:
            indexor.perform_indexing()

    def _remove_current_project(self):
        path = self._combo_projects.itemData(
            self._combo_projects.currentIndex())
        self._combo_projects.removeItem(self._combo_projects.currentIndex())

        self.main_window.remove_folder(path)
        initial_path = api.project.get_projects()[0]
        data = load_user_config(initial_path)
        try:
            linked_paths = data['linked_paths']
        except KeyError:
            linked_paths = []
        try:
            linked_paths.remove(path)
        except ValueError:
            _logger().warn('failed to remove linked path %r, path not in list',
                           path)
        finally:
            data['linked_paths'] = linked_paths
            save_user_config(initial_path, data)
            for indexor in self._indexors:
                if indexor.project == path:
                    self._indexors.remove(indexor)

    def _on_file_created(self, path):
        api.editor.open_file(path)
        project_path = self._combo_projects.itemData(self._combo_projects.currentIndex())

        with DbHelper() as dbh:
            try:
                dbh.create_file(path, project_id=index.get_project_ids([project_path])[0])
            except (TypeError, IndexError):
                return
            else:
                self._update_document_index(path)

    def _on_file_saved(self, path):
        self._update_document_index(path)

    def _update_document_index(self, path):
        file = index.get_file(path)
        if not file:
            return

        project = None
        for p in index.get_all_projects():
            if p.id == file.project_id:
                project = p
                break
        if not project:
            return
        test_path = 'file' + os.path.splitext(path)[1]
        plugin = get_symbol_parser(test_path, tuple(self.parser_plugins))
        if not plugin:
            return
        args = (path, file.id, project.path, project.id, plugin)
        api.tasks.start('Update file index', update_file, None, args=args)

    def _on_files_renamed(self, renamed_files):
        for old_path, new_path in renamed_files:
            old_path = os.path.normpath(os.path.normcase(old_path))
            new_path = os.path.normpath(os.path.normcase(new_path))
            self.main_window.tab_widget.rename_document(old_path, new_path)
            self.main_window.file_renamed.emit(old_path, new_path)
        api.tasks.start('Update renamed files index', rename_files, None,
                        args=(renamed_files,))

    def _on_files_deleted(self, deleted_files):
        for path in deleted_files:
            path = os.path.normpath(os.path.normcase(path))
            self.main_window.tab_widget.close_document(path)
            self.main_window.file_deleted.emit(path)
        api.tasks.start('Update renamed files index', delete_files, None,
                        args=(deleted_files,))

    @staticmethod
    def _on_locator_activated(path, line):
        if line == -1:
            line = None
        else:
            line -= 1  # 0 based
        api.editor.open_file(path, line=line)

    def _on_locator_cancelled(self):
        if self._locator.mode in [
                self._locator.MODE_GOTO_LINE, self._locator.MODE_GOTO_SYMBOL]:
            line, col = self._cached_cursor_position
            TextHelper(api.editor.get_current_editor()).goto_line(line, col)
