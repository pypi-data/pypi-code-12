"""
HackEdit use icons from theme (system theme on linux, breeze on Windows/OSX).

Breeze is a KDE specific icon theme with some additional non standard icons.
This module aims to provide a replacement for those missing icons.

Example of special icons:
    - code icons (code-variable, code-class,...)
    - debug icons (debug-step-into,...)
    - run/configure icons

"""
from PyQt5 import QtGui

from hackedit.api.utils import is_dark_theme


def configure_icon(build=False):
    """
    Gets the "configure" icon (for actions like configure project/build,...)
    """
    if build and QtGui.QIcon.hasThemeIcon('run-build-configure'):
        return QtGui.QIcon.fromTheme('run-build-configure')  # pragma: no cover
    if QtGui.QIcon.hasThemeIcon('configure'):
        return QtGui.QIcon.fromTheme('configure')
    else:  # pragma: no cover
        return QtGui.QIcon.fromTheme('applications-system')


def run_icon():
    """
    Gets the "run" icon (for actions like run script,...)

    :param build: True to get the run build icon.
    """
    if QtGui.QIcon.hasThemeIcon('debug-run'):
        return QtGui.QIcon.fromTheme('system-run')
    else:
        return QtGui.QIcon(':/icons/special/start.png')


def run_debug_icon():
    """
    Gets the "debug" icon (for actions like start debugging,...)
    """
    if QtGui.QIcon.hasThemeIcon('debug-run'):
        return QtGui.QIcon.fromTheme('debug-run')
    else:
        return QtGui.QIcon(':/icons/special/debugger_start.png')


def class_icon():
    """
    Gets the icon used to represent a "class" item.
    """
    return QtGui.QIcon.fromTheme(
        'code-class', QtGui.QIcon(':/icons/special/class.png'))


def variable_icon():
    """
    Gets the icon used to represent a "variable".
    """
    return QtGui.QIcon.fromTheme(
        'code-variable', QtGui.QIcon(':/icons/special/var.png'))


def function_icon():
    """
    Gets the icon used to represent a "function".
    """
    return QtGui.QIcon.fromTheme(
        'code-function', QtGui.QIcon(':/icons/special/func.png'))


def namespace_icon():
    """
    Gets the icon used to represent a "namespace".
    """
    return QtGui.QIcon.fromTheme(
        'code-context',
        QtGui.QIcon(':/icons/special/namespace.png'))


def object_locked():
    """
    Gets the object-locked icon.
    """
    if QtGui.QIcon.hasThemeIcon('object-locked'):
        icon_lock = QtGui.QIcon.fromTheme('object-locked')
    else:
        return QtGui.QIcon(':/icons/special/lock.png')
    return icon_lock


def object_unlocked():
    """
    Gets the object-unlocked icon.
    """
    if QtGui.QIcon.hasThemeIcon('object-unlocked'):
        icon_unlock = QtGui.QIcon.fromTheme('object-unlocked')
    else:
        return QtGui.QIcon(':/icons/special/unlock.png')
    return icon_unlock


def debug_step_into_icon():
    """
    Gets the "step into" debug icon.
    """
    if QtGui.QIcon.hasThemeIcon('debug-step-into'):
        return QtGui.QIcon.fromTheme('debug-step-into')
    else:
        return QtGui.QIcon(':/icons/special/debug-step-into.png')


def debug_step_over_icon():
    """
    Gets the "step over" debug icon.
    """
    if QtGui.QIcon.hasThemeIcon('debug-step-over'):
        return QtGui.QIcon.fromTheme('debug-step-over')
    else:
        return QtGui.QIcon(':/icons/special/debug-step-over.png')


def debug_step_out_icon():
    """
    Gets the "step out" debug icon.
    """
    if QtGui.QIcon.hasThemeIcon('debug-step-out'):
        return QtGui.QIcon.fromTheme('debug-step-out')
    else:
        return QtGui.QIcon(':/icons/special/debug-step-out.png')


def breakpoint_icon():
    """
    Gets the icon used to represent a breakpoint.
    """
    return QtGui.QIcon(':/icons/special/breakpoint.png')


def edit_breakpoints_icon():
    """
    Gets the icons used for the edit breakpoints action.
    """
    return QtGui.QIcon(':/icons/special/breakpoints.png')


def run_build():
    if QtGui.QIcon.hasThemeIcon('run-build'):
        return QtGui.QIcon.fromTheme('run-build')
    else:
        return QtGui.QIcon.fromTheme('system-run')


def build_clean():
    if QtGui.QIcon.hasThemeIcon('run-build-clean'):
        return QtGui.QIcon.fromTheme('run-build-clean')
    else:
        return QtGui.QIcon.fromTheme('edit-clear')


def app_menu():
    if QtGui.QIcon.hasThemeIcon('application-menu'):
        return QtGui.QIcon.fromTheme('application-menu')
    else:
        return QtGui.QIcon.fromTheme('open-menu-symbolic')
