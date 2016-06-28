"""
This package contains the COBOL plugins entrypoints.
"""
from PyQt5 import QtGui
from pyqode.core.widgets import ErrorsTable
from pyqode.core.modes import CheckerMessages

ErrorsTable.ICONS = {
    CheckerMessages.INFO: QtGui.QIcon.fromTheme('dialog-information'),
    CheckerMessages.WARNING: QtGui.QIcon.fromTheme('dialog-warning'),
    CheckerMessages.ERROR: QtGui.QIcon.fromTheme('dialog-error'),
}
