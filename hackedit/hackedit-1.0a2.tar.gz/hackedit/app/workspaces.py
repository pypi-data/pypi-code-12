import glob
import json
import logging
import os

import pkg_resources

from hackedit.api import system, plugins


def _logger():
    return logging.getLogger(__name__)


class WorkspaceManager:
    """
    Manage the list of available workspace.
    """
    builtin_workspaces = None

    def __init__(self):
        WorkspaceManager.load_builtin_workspaces()
        self._workspaces = {value['name']: value for value in
                            WorkspaceManager.builtin_workspaces}
        self._load_user_workspaces()

    @classmethod
    def load_builtin_workspaces(cls):
        _logger().debug('loading builtin plugins')
        if cls.builtin_workspaces is None:
            cls.builtin_workspaces = []
            for entrypoint in pkg_resources.iter_entry_points(
                    plugins.WorkspaceProviderPlugin.ENTRYPOINT):
                _logger().debug('  - loading builtin workspace: %s',
                                entrypoint)
                try:
                    workspace = entrypoint.load()().get_data()
                except (ImportError, TypeError):
                    _logger().exception('failed to import builtin workspace')
                else:
                    workspace['editable'] = False
                    cls.builtin_workspaces.append(workspace)
                    _logger().debug('  - builtin workspace loaded: %s',
                                    entrypoint)
        _logger().debug('builtin workspaces: %r', cls.builtin_workspaces)

    def _load_user_workspaces(self):
        user_folder = system.get_user_workspaces_dir()
        _logger().debug('inspecting user folder: %s', user_folder)
        for file in glob.glob(os.path.join(user_folder, '*.json')):
            _logger().debug('  - loading workspace: %s', file)
            try:
                with open(file) as fp:
                    workspace = json.load(fp)
                workspace['editable'] = os.access(file, os.W_OK)
                workspace['path'] = file
                name = workspace['name']
                if name in self._workspaces:
                    _logger().debug('workspace conflict: a workspace with '
                                    'the same name already exists')
                else:
                    self._workspaces[name] = workspace
            except (OSError, ValueError):
                _logger().exception('failed to load workpsace')
            else:
                _logger().debug('workspace loaded: %r', workspace)

    def get_names(self):
        """
        Gets all workspace names.
        :return: List of str
        """
        return sorted(list(self._workspaces.keys()))

    def workspace_by_name(self, name):
        """
        Gets a workspace by name
        :param name: name of the workspace to retrieve.
        :return: dict or None
        """
        for workspace in self._workspaces.values():
            if workspace['name'] == name:
                return workspace
        return None
