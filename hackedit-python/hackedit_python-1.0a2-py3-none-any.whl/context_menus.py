"""
This plugin add additional actions to the filesystem context menu
specific to python (create package, create module,...).
"""
import logging
import mimetypes
import os

from PyQt5 import QtGui, QtWidgets
from hackedit import api
from hackedit.api import plugins, special_icons, interpreters, window
from pyqode.core.widgets import FileSystemHelper


_ = api.gettext.get_translation(package='hackedit-python')


class PyContextMenus(plugins.WorkspacePlugin):
    """
    This plugins add some python specific actions to the project tree view
    context menu, the tab bar context menu and the editor context menu.
    """
    project_only = True

    def activate(self):
        self._tree_view = window.get_project_treeview()
        self._py_run = plugins.get_plugin_instance(
            api.interpreters.ScriptRunnerPlugin)
        self._setup_treeview_actions()
        self._setup_tab_context_menu(window.get_main_window())

    def _setup_tab_context_menu(self, window):
        """
        Setup tab bar context menu
        """
        sep = QtWidgets.QAction(self.main_window)
        sep.setSeparator(True)
        api.window.add_tab_widget_context_menu_action(sep)

        action = QtWidgets.QAction(_('Run'), window)
        action.setToolTip(_('Run active configuration.'))
        action.triggered.connect(self._on_run_from_tab)
        action.setIcon(special_icons.run_icon())
        api.window.add_tab_widget_context_menu_action(action)

        action = QtWidgets.QAction(_('Configure'), window)
        action.setToolTip(_('Change active configuration.'))
        action.triggered.connect(self._on_configure_from_tab)
        action.setIcon(special_icons.configure_icon())
        api.window.add_tab_widget_context_menu_action(action)

    def _setup_treeview_actions(self):
        """
        Setup project tree view context menu actions
        """
        insert_point = self._tree_view.context_menu.action_create_file
        # New module
        self._action_new_module = QtWidgets.QAction(_('&Module'),
                                                    self.main_window)
        self._action_new_module.setToolTip(_('Create a new python module'))
        self._action_new_module.setIcon(
            api.widgets.FileIconProvider.mimetype_icon('file.py'))
        self._action_new_module.triggered.connect(
            self._on_new_module_triggered)
        self._tree_view.context_menu.menu_new.insertAction(
            insert_point, self._action_new_module)
        # New package
        self._action_new_package = QtWidgets.QAction(_('&Package'),
                                                     self.main_window)
        self._action_new_package.setToolTip(_('Create a new python package'))
        self._action_new_package.setIcon(
            QtGui.QIcon.fromTheme('folder'))
        self._action_new_package.triggered.connect(
            self._on_new_package_triggered)
        self._tree_view.context_menu.menu_new.insertAction(
            insert_point, self._action_new_package)
        # separator with the regular entries
        separator = QtWidgets.QAction(self.main_window)
        separator.setSeparator(True)
        self._tree_view.context_menu.menu_new.insertAction(
            insert_point, separator)

        insert_pt = self._tree_view.context_menu.menu_new.menuAction()

        action = QtWidgets.QAction(_('Run file'), self.main_window)
        action.setToolTip(_('Automatically configure and run selected file.'))
        action.setIcon(special_icons.run_icon())
        action.triggered.connect(self._on_run_file_triggered)
        self._tree_view.context_menu.insertAction(insert_pt, action)
        self.tv_action_run = action

        action = QtWidgets.QAction(_('Configure file'), self.main_window)
        action.setToolTip(_('Create/edit run configuration for the '
                            'selected file.'))
        action.setIcon(special_icons.configure_icon())
        action.triggered.connect(self._on_configure_file_triggered)
        self._tree_view.context_menu.insertAction(insert_pt, action)
        self.tv_action_configure = action

        separator = QtWidgets.QAction(self.main_window)
        separator.setSeparator(True)
        self._tree_view.context_menu.insertAction(insert_pt, separator)
        self.tv_action_sep = separator

        self._tree_view.about_to_show_context_menu.connect(
            self._on_about_to_show_tv_context_menu)

    def _on_about_to_show_tv_context_menu(self, path):
        is_python = mimetypes.guess_type(path)[0] == 'text/x-python'
        self.tv_action_configure.setVisible(is_python)
        self.tv_action_run.setVisible(is_python)
        self.tv_action_sep.setVisible(is_python)

    def _on_new_module_triggered(self):
        src = self._tree_view.helper.get_current_path()
        if os.path.isfile(src):
            src = os.path.dirname(src)
        name, status = QtWidgets.QInputDialog.getText(
            self._tree_view, _('Create new python module'), _('Module name:'),
            QtWidgets.QLineEdit.Normal, _('my_module'))
        if status:
            if not os.path.splitext(name)[1]:
                name += '.py'
            path = os.path.join(src, name)
            try:
                with open(path, 'w'):
                    pass
            except OSError:
                _logger().exception('failed to create new python module')
            else:
                self._tree_view.file_created.emit(path)

    def _on_new_package_triggered(self):
        src = self._tree_view.helper.get_current_path()
        if os.path.isfile(src):
            src = os.path.dirname(src)
        name, status = QtWidgets.QInputDialog.getText(
            self._tree_view, _('Create new python package'),
            _('Package name:'),
            QtWidgets.QLineEdit.Normal, _('my_package'))
        if status:
            path = os.path.join(src, name)
            try:
                os.makedirs(path)
                path = os.path.join(path, '__init__.py')
                with open(path, 'w'):
                    pass
            except OSError:
                _logger().exception('failed to create new python package')
            else:
                self._tree_view.file_created.emit(path)

    def _create_default_config(self, path):
        project = None
        for p in api.project.get_projects():
            p += os.sep
            if p in path:
                project = p
                break
        if project is None:
            project = api.project.get_current_project()
        configs = interpreters.load_configs(project)
        config = interpreters.create_default_config(path)
        exist = False
        for cfg in configs:
            if cfg['name'] == config['name']:
                exist = True
                break
        if not exist:
            configs.append(config)
            interpreters.save_configs(project, configs)
        projects = api.project.get_projects()
        interpreters.save_active_config(projects[0], config['name'])
        self._py_run.refresh()

    def _on_run_from_tab(self):
        path = api.window.get_tab_under_context_menu().file.path
        self._run_file(path)

    def _on_run_file_triggered(self):
        path = FileSystemHelper(self._tree_view).get_current_path()
        self._run_file(path)

    def _run_file(self, path):
        if os.path.isfile(path):
            self._create_default_config(path)
            self._py_run.run()
            self._py_run.refresh()
            self._py_run.enable_mnu_configs()
            self._py_run.enable_run()

    def _on_configure_from_tab(self):
        path = api.window.get_tab_under_context_menu().file.path
        self._configure_file(path)

    def _on_configure_file_triggered(self):
        path = FileSystemHelper(self._tree_view).get_current_path()
        self._configure_file(path)

    def _configure_file(self, path):
        if os.path.isfile(path):
            self._create_default_config(path)
            self._py_run.configure()


def _logger():
    return logging.getLogger(__name__)
