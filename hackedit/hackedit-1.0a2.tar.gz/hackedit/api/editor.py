"""
This module contains an API for interacting with the main window's editors.
"""
from ._shared import _window


def open_file(path, line=None, column=0):
    """
    Opens a file in a new editor.

    If the file was already open, the existing editor instance is returned.

    :param path: file path to open in a new editor.
    :param line: line to go to (optional).
    :param line: column to go to (optional).

    :return: The editor widget instance that has been created.
    :rtype: pyqode.core.api.CodeEdit
    """
    return _window().open_file(path, line, column)


def get_current_editor():
    """
    Returns the current editor widget.

    :rtype: pyqode.core.api.CodeEdit
    """
    return _window().current_tab


def get_current_path():
    """
    Returns the path of the current editor.
    """
    tab = _window().current_tab
    if tab is not None:
        return tab.file.path
    return None


def get_all_editors(include_clones=False):
    """
    Returns the list of all the open editors.

    :param include_clones: True to include cloned editors (split)
    :returns: a list of CodeEdit
    :rtype: list
    """
    return _window().tab_widget.widgets(include_clones=include_clones)


def get_all_paths():
    """
    Returns the list of all the open editor paths.

    :returns: a list of paths
    :rtype: list of str
    """
    return [w.file.path for w in _window().tab_widget.widgets()
            if hasattr(w, 'file') and hasattr(w.file, 'path')]


def save_current_editor_as():
    """
    Saves the current editor as (the save as dialog will be shown
    automatically).
    """
    _window().save_current_as()


def save_current_editor():
    """
    Saves the current editor.
    """
    _window().save_current()


def save_all_editors():
    """
    Saves all editors.
    """
    _window().save_all()
