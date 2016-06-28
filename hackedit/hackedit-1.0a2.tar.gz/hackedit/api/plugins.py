"""
This module contains the plugin interface that you need to implement
for writing new plugins.

Plugins are regular python packages that contains a set of setuptools
entrypoints that expose the available plugins.

Basically you need to define a dictionary where the keys are the possible
entrypoints (one per plugin type) and the values the list of python classes
that implement the entrypoint interface.

This module describes the entrypoints interface, each "interface" has a
``ENTRYPOINT`` attribute, that is the string you need to use in the entrypoints
dict in your setup.py.

"""
from PyQt5.QtCore import QObject

from ._shared import _window


class EditorPlugin:
    """
    An editor plugin returns the CodeEdit class that needs to be registerd
    inside the application.
    """
    #: setuptools entry point to use for adding new editor plugins.
    ENTRYPOINT = 'hackedit.plugins.editors'

    @staticmethod
    def get_editor_class():
        """
        Returns the editor **class** to register.
        :return: a subclass of :class:`pyqode.core.api.CodeEdit`
        """
        pass

    @classmethod
    def get_specific_preferences_page(cls):
        """
        Returns a preferences page to edit the settings specific to your
        editor.
        """
        pass

    @classmethod
    def apply_specific_preferences(cls, editor):
        """
        Apply the specific preferences to an editor instance
        """
        pass


class FileIconProviderPlugin:
    """
    The file icon provider plugin provide a custom icon for a specific file
    extension. Implement this only if the mimetype for your file is not widely
    available in the icon themes.

    To define such a plugin, you need to define a list of supported
    extensions: :attr:SUPPORTED_EXTENSIONS and a function that will return the
    actual QIcon instance: :func:`icon`.
    """
    ENTRYPOINT = 'hackedit.plugins.file_icon_providers'

    #: the list of supported file extensions. Use the '.' extension for
    #: folders (e.g. if you need to display a custom icon for special folders
    #: such as python packages).
    SUPPORTED_EXTENSIONS = []

    def icon(self, file_info):
        """
        Returns the corresponding file icon

        :param file_info: QFileInfo
        :retype: PyQt5.QtGui.QIcon
        """
        pass


class WorkspacePlugin(QObject):
    """
    A workspace plugin is a generic window plugin but tied to a workspace.

    To create a workspace plugin: create a subclass and implement the following
    methods:

        - activate: setup your plugin
        - close: to stop any background task or close any resource that your
          plugin might use.
        - get_preferences_page (classmethod): returns a custom
          :class:`hackedit.widgets.PreferencePage` instance that will show up
          in the app's preferences dialog.
        - apply_preferences: to apply any custom preferences exposed by
          :func:`get_preferences_page` on the plugin instance.

    """

    #: setuptools entry point to use for adding new editor plugins.
    ENTRYPOINT = 'hackedit.plugins.workspace_plugins'

    def __init__(self, window):
        """
        :param window: Reference to the main window where the plugin has been
                       attached to.
        :type window: hackedit.app.gui.main_window.MainWindow
        """
        self.main_window = window
        super().__init__()

    def activate(self):
        """
        Activates the plugin.

        You should implement this method to setup your plugin (create widgets,
        connect signals/slots,...)
        """
        pass

    def close(self):
        """
        This method is called when the parent window has been closed.

        Implemented this method if you need to cleanup some resources or stop
        somes services,...
        """
        pass

    @classmethod
    def get_preferences_page(cls):
        """
        Returns the plugin config page. A page is a simple widget where you
        expose your plugin's preferences. That page will be automatically shown
        under the plugin node in the application's preferences dialog.

        .. warning: This is a classmethod!

        :rtype: hackedit.api.widgets.PreferencePage
        """
        pass

    def apply_preferences(self):
        """
        Apply user preferences to your plugin (the one exposed in your config
        page).
        """
        pass


class WorkspaceProviderPlugin:
    """
    A workspace provider plugin let you add some builtin workspaces to
    HackEdit.

    Just implement `get_data` to return a dictionary with the following
    structure::

        workspace = {
            name: 'Your workspace name',
            description: 'Your workspace description, can be multiline',
            plugins: ['PluginA', 'PluginB', ...]
        }

    """

    #: setuptools entry point to use for adding new editor plugins.
    ENTRYPOINT = 'hackedit.plugins.workspace_providers'

    def get_data(self):
        """
        Gets the workspace data dictionnary.
        """
        pass


class SymbolParserPlugin:
    """
    Plugin used to parse the symbols of a file.

    The plugin must declare the mimetypes it can handle and implement
    the ``parse`` method.

    The parse method will parse the content of a file and return a list
    of :class:`pyqode.core.share.Definition` that will be written to the
    project's index database by the indexing backend.
    """
    ENTRYPOINT = 'hackedit.plugins.symbol_parsers'

    #: Specify the mimetypes that can be handled by a particular indexor
    #: plugin
    mimetypes = []

    def parse(self, path):
        """
        Parses a file and returns a list of
        :class:`pyqode.core.share.Definition`.

        This method will be called automatically when indexing files for any
        file that match one of the supported mimetype.
        """
        pass


class PreferencePagePlugin:
    """
    A preference page plugin provides a :class:`PreferencePage` widget that
    will get automatically shown in the application preferences dialog.

    This preference page won't be tied to the plugins category (you're free to
    define a category or not in your preferences page).
    """

    #: setuptools entry point to use for adding new editor plugins.
    ENTRYPOINT = 'hackedit.plugins.preference_pages'

    @classmethod
    def get_preferences_page(cls):
        """
        Returns the preference page widget.
        """
        pass


class TemplateProviderPlugin:
    """
    A template provider plugin provides an additional source of templates
    to the application.
    """
    ENTRYPOINT = 'hackedit.plugins.template_providers'

    def get_label(self):
        """
        Gets the label of the provider. The label will appear in the list
        of template sources. It must be carefully chosen.
        """
        pass

    def get_url(cls):
        """
        Gets the template url. This can be a remote url (pointing to a git
        repository) or a local url (pointing to the directory that contains the
        templates)
        """
        pass


def get_plugin_instance(plugin_class):
    """
    Returns the plugin instance that match a given plugin **class**.

    :param plugin_class: Plugin class
    """
    return _window().get_plugin_instance(plugin_class)


def get_script_runner():
    """
    Gets the script runner plugin instance if any otherwise returns None.

    :rtype: hackedit.api.interpreters.ScriptRunnerPlugin
    """
    from .interpreters import ScriptRunnerPlugin

    return _window().get_plugin_instance(ScriptRunnerPlugin)
