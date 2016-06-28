"""
This module contains a high level procedural API for interacting with the main
window.

"""
import logging

from ._shared import _window


def add_tab_widget_context_menu_action(action):
    """
    Adds an action to the tab widget context menu.

    :param action: Action to add.
    """
    _window().tab_widget.add_context_action(action)


def get_tab_under_context_menu():
    """
    Returns the editor tab widget that is under the tab widget
    context menu. If context menu is not visible, this function
    returns None
    :rtype: pyqode.core.api.CodeEdit
    """
    return _window().tab_widget.tab_under_menu


def add_dock_widget(widget, title, icon=None, area=None, special=False):
    """
    Adds a new dock widget to the window.

    This function will create a new QDockWidget to display ``widget``.

    A control button will automatically be added to the corresponding
    dock window manager. You can access this button through the ``button``
    attribute of the returned dock widget instance.

    :param widget: the widget to dock (QWidget, not a QDockWidget)
    :param title: dock widget title
    :param icon: dock widget icon
    :param area: dock widget area
    :param special: Special flag for bottom area, if True the dock widget
        button will be added at the end of the toolbar instead of the
        beginning. False by default.

    :return The dock widget instance that was added to the window.
    :rtype: PyQt5.QtWidgets.QDockWidget
    """
    return _window().add_dock_widget(widget, title, icon, area, special)


def remove_dock_widget(dockwidget):
    """
    Removes a dock widget
    :param dockwidget: dock widget to remove
    :return:
    """
    _window().removeDockWidget(dockwidget)


def add_action(action):
    """
    Adds an action to the window
    :param action: QAction
    """
    _window().addAction(action)


def add_actions(actions):
    """
    Adds a list actions to the window
    :param action: list of QAction
    """
    _window().addActions(actions)


def get_main_window():
    """
    Gets the bound window.

    :rtype: hackedit.app.main_window.MainWindow
    """
    return _window()


def get_main_window_ui():
    """
    Gets the user interface object of the main window.

    :rtype: hackedit.app.forms.main_window_ui.Ui_MainWindow
    """
    return _window().ui


def get_tray_icon():
    """
    Gets the application tray icon instance

    :rtype: PyQt5.QtWidgets.QSystemTrayIcon
    """
    return _window().app.tray_icon


def get_menu(menu_name):
    """
    Gets a top level menu.

    The menu is implicitly created if it did not exist.

    :param menu_name: Name of the menu to retrieve.

    :rtype: PyQt5.QtWidgets.QMenu
    """
    return _window().get_menu(menu_name)


def get_toolbar(name, title):
    """
    Gets a toolbar. The toolbar is implicitly created if it did not exist.

    :param name: Name of the toolbar
    :param title: Title of the toolbar (used when creating the toobar).
    :rtype: PyQt5.QtWidgets.QToolBar
    """
    return _window().get_toolbar(name, title)


def get_dock_widget(title):
    """
    Returns the dock widget where `windowTitle` match `title`.

    :param title: title of the dock widget to get.
    :return: PyQt5.QtWidgets.QDockWidget
    """
    return _window().get_dock_widget(title)


def get_project_treeview():
    """
    Gets the project treeview.

    :return: pyqode.core.widgets.FileSystemTreeView
    """
    return _window().get_project_treeview()


def add_statusbar_widget(widget, first=False):
    """
    Add a widget to the status bar.

    :param widget: widget to add
    """
    return _window().add_statusbar_widget(widget, first=first)


def restore(window):
    """
    Restores a window:

        - shows the window
        - raises the awindow
        - activates the window

    :param window: window to restore
    :type window: PyQt5.QtWidgets.QMainWindow
    """
    if window.isMinimized():
        window.showNormal()
    else:
        window.show()
    window.activateWindow()
    window.raise_()


def get_run_widget():
    """
    Gets the run widget currently visible or create one if the run dock widget
    has been removed.
    """
    from hackedit import api
    w = _window()
    run_dock = w.get_dock_widget(_('Run'))
    if not run_dock:
        w.run_widget = api.widgets.RunWidget(w)
        w.run_widget.last_tab_closed.connect(_remove_run_dock)
        w.run_dock = api.window.add_dock_widget(
            w.run_widget, _('Run'), api.special_icons.run_icon())
        w.run_dock.run_widget = w.run_widget
    else:
        w.run_dock = run_dock
        w.run_widget = run_dock.run_widget
    return w.run_widget


def _remove_run_dock():
    w = _window()
    w.removeDockWidget(w.run_dock)
    w.run_dock.run_widget = None
    w.run_widget = None
    w.run_dock = None


def __logger():
    return logging.getLogger(__name__)
