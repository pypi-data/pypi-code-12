"""
This module contains the plugins manager that loads and store the various
plugins.
"""
import logging
import traceback

import pkg_resources
from pyqode.core.widgets import SplittableCodeEditTabWidget

from hackedit.api import plugins, events
from hackedit.api.widgets import FileIconProvider


def _logger():
    return logging.getLogger(__name__)


class LoadPluginFailedEvent(events.ExceptionEvent):
    def __init__(self, title, description, exception, tb=None,
                 custom_actions=None):
        super().__init__(title, description, exception, tb, custom_actions)
        self.level = events.WARNING


class PluginManager:
    """
    Loads and stores the various kind of plugins.

    Plugins are setuptools entrypoints (see
    https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins).

    The plugin manager is instantiated **once** in
    :class:`hackedit.app.Application`.
    """
    def __init__(self):
        #: Map of workspace plugin classes
        self.workspace_plugins = {}
        #: List of window plugins.
        self.window_plugins = []
        #: List of preference pages plugins
        self.preferences_page_plugins = []
        #: The list of editor plugins classes
        self.editor_plugins = []
        #: The list of template provider plugins
        self.template_providers = []
        #: the map of plugin which failed to load with their traceback
        self.failed_to_load = {}
        self._load_template_provider_plugins()
        self._load_editor_plugins()
        self._load_preferences_page_plugins()
        self._load_workspace_plugins()
        FileIconProvider.load_plugins()
        SplittableCodeEditTabWidget.icon_provider_klass = FileIconProvider

    def _load_workspace_plugins(self):
        """
        Loads workspace plugins (plugins that are tied to a specific worskpace)
        """
        _logger().info('loading workspace plugins')
        entrypoints = list(pkg_resources.iter_entry_points(
            plugins.WorkspacePlugin.ENTRYPOINT))
        for entrypoint in entrypoints:
            _logger().info('  - loading plugin: %s', entrypoint)
            try:
                plugin_class = entrypoint.load()
            except Exception as e:
                _logger().exception('Failed to load workspace plugin')
                name = str(entrypoint).split('=')[0].strip()
                self.failed_to_load[name] = traceback.format_exc(), e
            else:
                self.workspace_plugins[plugin_class.__name__] = plugin_class
        _logger().debug('available workspace plugins: %r',
                        self.workspace_plugins)

    def _load_preferences_page_plugins(self):
        """
        Loads preferences pages plugins.
        """
        _logger().info('loading preferences pages plugins')
        entrypoints = list(pkg_resources.iter_entry_points(
            plugins.PreferencePagePlugin.ENTRYPOINT))
        for entrypoint in entrypoints:
            _logger().info('  - loading plugin: %s', entrypoint)
            try:
                plugin_class = entrypoint.load()
            except Exception as e:
                _logger().exception('failed to load preferences page plugin')
                name = str(entrypoint).split('=')[0].strip()
                self.failed_to_load[name] = traceback.format_exc(), e
            else:
                self.preferences_page_plugins.append(plugin_class)
        _logger().debug('preferences page plugins: %r',
                        self.preferences_page_plugins)

    def _load_template_provider_plugins(self):
        """
        Loads preferences pages plugins.
        """
        _logger().info('loading template provider plugins')
        entrypoints = list(pkg_resources.iter_entry_points(
            plugins.TemplateProviderPlugin.ENTRYPOINT))
        for entrypoint in entrypoints:
            _logger().info('  - loading plugin: %s', entrypoint)
            try:
                plugin_class = entrypoint.load()
            except Exception as e:
                _logger().exception('failed to load template provider plugin')
                name = str(entrypoint).split('=')[0].strip()
                self.failed_to_load[name] = traceback.format_exc(), e
            else:
                self.template_providers.append(plugin_class())
        _logger().debug('template providers plugins: %r',
                        self.template_providers)

    def _load_editor_plugins(self):
        """
        Loads editor plugins.
        """
        _logger().info('loading editor plugins')
        entrypoints = list(pkg_resources.iter_entry_points(
            plugins.EditorPlugin.ENTRYPOINT))
        for entrypoint in entrypoints:
            _logger().info('  - loading plugin: %s', entrypoint)
            try:
                plugin_class = entrypoint.load()
            except Exception as e:
                _logger().exception('Failed to load editor plugin')
                name = str(entrypoint).split('=')[0].strip()
                self.failed_to_load[name] = traceback.format_exc(), e
            else:
                try:
                    klass = plugin_class.get_editor_class()
                except AttributeError as e:
                    _logger().exception(
                        'invalid editor plugin: register_editor not '
                        'implemented')
                    self.failed_to_load[name] = traceback.format_exc(), e
                else:
                    SplittableCodeEditTabWidget.register_code_edit(klass)
                    self.editor_plugins.append(plugin_class)
