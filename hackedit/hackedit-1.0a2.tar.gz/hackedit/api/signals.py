"""
This module contains the list of signals that you can connect to and the
functions to connect/disconnect a slot to a signal.


Example::

    from hackedit import api

    def on_editor_loaded(editor):
        print(editor)


    api.signals.connect_slot(api.signals.EDITOR_LOADED, on_editor_loaded)

"""
import logging

from ._shared import _window


#: Signal emitted when the window state has been restored.
#: Tools that needs to automatically hide could hook up this signal...
STATE_RESTORED = 'state_restored'

#: Signal emitted when the window has been closed.
#:
#: Parameters:
#:     - window instance (QMainWindow)
WINDOW_CLOSED = 'closed'

#: Signal emitted when the current tab changed.
#:
#: Parameters:
#:     - editor instance (pyqode.core.CodeEdit)
CURRENT_EDITOR_CHANGED = 'current_tab_changed'

#: Signal emitted just before creating an new editor.
#:
#: Parameters:
#:     - file path (str)
ABOUT_TO_OPEN_EDITOR = 'about_to_open_tab'

#: Signal emitted when a new editor has been created, but the file content
#: has not been loaded yet.
#:
#: Parameters:
#:     - editor instance (pyqode.core.CodeEdit)
EDITOR_CREATED = 'editor_created'

#: Signal emitted when an editor has been detached. Since a new instance is
#: created, you might need to change some of the properties of the new editor.
#:
#: Parameters:
#:     - old_tab: the old tab instance (before it is closed)
#:     - new_tab: the new tab instance (i.e. the one that is detached)
EDITOR_DETACHED = 'editor_detached'

#: Signal emitted when a new editor has been created and the file content
#: has been loaded.
#:
#: Parameters:
#:     - editor instance (pyqode.core.CodeEdit)
EDITOR_LOADED = 'editor_loaded'

#: Signal emitted when a project (directory) has been added to the window.
#:
#: Parameters:
#:      - project path (str)
PROJECT_ADDED = 'project_added'

#: Signal emitted when the current project changed.
#:
#: Parameters:
#:      - project path (str)
CURRENT_PROJECT_CHANGED = 'current_project_changed'

#: Signal emitted when a document has been saved.
#:
#: Parameters:
#:    - save_file_path
#:    - old_content
DOCUMENT_SAVED = 'document_saved'

#: Signal emitted when the list of project files (generated in a background
#: process) is available.
#:
#: This list is initially emtpy.
#:
#: *Note this list is being generated and refreshed by the project
#: explorer plugin, if this plugin is not loaded in a workspace then the
#: list will remain empty and this signal will never be emitted.*
PROJECT_FILES_AVAILABLE = 'project_files_available'


#: Signal emitted when a project file has been renamed
#: Parameters:
#:     - old_name (str)
#:     - new_name (str)
FILE_RENAMED = 'file_renamed'

#: Signal emitted when a project file has been removed
#: Parameters:
#:     - file path
FILE_DELETED = 'file_deleted'


#: The list of valid signals.
SIGNALS = [
    STATE_RESTORED,
    WINDOW_CLOSED,
    CURRENT_EDITOR_CHANGED,
    ABOUT_TO_OPEN_EDITOR,
    EDITOR_CREATED,
    EDITOR_DETACHED,
    EDITOR_LOADED,
    PROJECT_ADDED,
    CURRENT_PROJECT_CHANGED,
    DOCUMENT_SAVED,
    PROJECT_FILES_AVAILABLE,
    FILE_RENAMED,
    FILE_DELETED
]


def connect_slot(signal, slot):
    """
    Connects a slot to a given signal.

    :param signal: Signal to connect to
    :param slot: callable object that will get called when the signal is
                 emitted.

    :raise: ValueError if ``signal`` is not valid.
    """
    if signal not in SIGNALS:
        raise ValueError('%r is not a valid signal' % signal)
    w = _window()
    getattr(w, signal).connect(slot)


def disconnect_slot(signal, slot):
    """
    Disconnects a slot from a given signal.

    :param signal: Signal to disconnect from.
    :param slot: slot to disconnect
    :raise: ValueError if ``signal`` is not valid.
    """
    if signal not in SIGNALS:
        raise ValueError('%r is not a valid signal' % signal)
    try:
        getattr(_window(), signal).disconnect(slot)
    except (TypeError, RuntimeError):  # pragma: no cover
        # already disconnected
        __logger().warn('failed to disconnect slot %r from signal %r',
                        slot, signal)


def __logger():
    return logging.getLogger(__name__)
