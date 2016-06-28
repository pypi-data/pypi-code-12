"""
**Internal** helper module shared by most api modules to retrieve the current
MainWindow instance.
"""
import inspect

from PyQt5 import QtWidgets


APP = None


def _window():
    """
    Retrieves window instance from the caller object (usually a WorkspacePlugin
    or a WindowPlugin).

    If there is no caller object, the active window is used, this allow
    to hack HackEdit from the developer console!

    This is used to simplify the public API: plugins don't need to pass
    the `window` parameter to the public API functions everytime...

    :rtype: hackedit.app.main_window.MainWindow
    """
    def caller():
        frame = inspect.stack()[3][0]
        caller = frame.f_locals.get('self')
        return caller

    from hackedit.app.main_window import MainWindow

    try:
        w = caller().main_window
        if w and isinstance(w, MainWindow):
            return w
        raise AttributeError('main_window is None')
    except (AttributeError, IndexError):
        # not from a plugin, use active window instead
        w = QtWidgets.qApp.activeWindow()
        if not isinstance(w, MainWindow):
            try:
                w = APP.active_window
            except IndexError:
                w = None
        return w
