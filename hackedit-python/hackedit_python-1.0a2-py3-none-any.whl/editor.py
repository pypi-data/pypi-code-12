"""
Registers PyCodeEdit to the application's tab widget.
"""
import logging
import mimetypes
import os
import sys

from PyQt5 import QtCore, QtGui
from hackedit import api
from hackedit.api import plugins
from pyqode.core import api as pyqode_api, modes, panels
from pyqode.core.api import ColorScheme
from pyqode.python import modes as pymodes, panels as pypanels
from pyqode.python.backend.workers import defined_names
from pyqode.python.folding import PythonFoldDetector
from pyqode.python.widgets import PyCodeEditBase

from hackedit_python.add_import import AddImportMode
from hackedit_python.forms import settings_page_editor_ui
from hackedit_python import pyqode_server as server


_ = api.gettext.get_translation(package='hackedit-python')


# add pyw to the list of mime types
mimetypes.add_type('text/x-python', '.pyw')


def _logger():
    return logging.getLogger(__name__)


def _get_backend_libs_path():
    return os.environ['HACKEDIT_VENDOR_PATH']


class DisplayEditor(PyCodeEditBase):
    """
    Extends PyCodeEditBase with a set of hardcoded modes and panels specifics
    to a python code editor widget.
    """
    mimetypes = ['text/x-python']

    def __init__(self, parent=None, color_scheme='qt'):
        super().__init__(parent=parent)
        # panels
        self.panels.append(panels.FoldingPanel())
        self.panels.append(panels.LineNumberPanel())
        self.panels.append(panels.CheckerPanel())
        self.panels.append(panels.GlobalCheckerPanel(),
                           panels.GlobalCheckerPanel.Position.RIGHT)
        # modes
        self.modes.append(modes.RightMarginMode())
        self.caret_highlighter = self.modes.append(
            modes.CaretLineHighlighterMode())
        self.modes.append(pymodes.PythonSH(
            self.document(), color_scheme=ColorScheme(color_scheme)))
        self.syntax_highlighter.fold_detector = PythonFoldDetector()
        self.breakpoints_panel = self.panels.append(panels.MarkerPanel())


class PyCodeEdit(PyCodeEditBase):
    """
    Extends PyCodeEditBase with a set of hardcoded modes and panels specifics
    to a python code editor widget.
    """
    mimetypes = ['text/x-python']

    BACKEND_INTERPRETER = sys.executable
    BACKEND_SERVER = server.__file__
    BACKEND_ARGS = None

    def __init__(self, parent=None, color_scheme='qt'):
        super().__init__(parent=parent)
        self.setLineWrapMode(self.NoWrap)
        # install those modes first as they are required by other modes/panels
        self.modes.append(modes.OutlineMode(defined_names))

        # panels
        self.panels.append(panels.SearchAndReplacePanel(),
                           panels.SearchAndReplacePanel.Position.BOTTOM)
        self.panels.append(panels.FoldingPanel())
        self.panels.append(panels.LineNumberPanel())
        self.panels.append(panels.CheckerPanel())
        self.panels.append(panels.GlobalCheckerPanel(),
                           panels.GlobalCheckerPanel.Position.RIGHT)
        # modes
        # generic
        self.modes.append(modes.CursorHistoryMode())
        self.modes.append(modes.ExtendedSelectionMode())
        self.modes.append(modes.CaseConverterMode())
        self.modes.append(modes.CaretLineHighlighterMode())
        self.modes.append(modes.FileWatcherMode())
        self.modes.append(modes.RightMarginMode())
        self.modes.append(modes.ZoomMode())
        self.modes.append(modes.SymbolMatcherMode())
        self.modes.append(modes.CodeCompletionMode())
        self.modes.append(modes.OccurrencesHighlighterMode())
        self.modes.append(modes.SmartBackSpaceMode())
        # python specifics
        self.modes.append(pymodes.PyAutoIndentMode())
        self.modes.append(pymodes.PyAutoCompleteMode())
        self.modes.append(pymodes.FrostedCheckerMode())
        self.modes.append(pymodes.PEP8CheckerMode())
        self.modes.append(pymodes.CalltipsMode())
        self.modes.append(pymodes.PyIndenterMode())
        self.add_separator()
        self.modes.append(AddImportMode())
        self.modes.append(pymodes.GoToAssignmentsMode())
        self.modes.append(pymodes.CommentsMode())
        self.modes.append(pymodes.PythonSH(
            self.document(), color_scheme=ColorScheme(color_scheme)))
        self.syntax_highlighter.fold_detector = PythonFoldDetector()

        self.panels.append(pypanels.QuickDocPanel(),
                           pyqode_api.Panel.Position.BOTTOM)
        self.panels.append(panels.EncodingPanel(),
                           pyqode_api.Panel.Position.TOP)

        self.breakpoints_panel = self.panels.append(panels.MarkerPanel())
        self.line_highlighter = self.modes.append(modes.LineHighlighterMode())

        self.restart_backend()

    def restart_backend(self):
        """
        Restarts the backend process using:
            - PyCodeEdit.BACKEND_SERVER
            - PyCodeEdit.BACKEND_INTERPRETER
            - PyCodeEdit.BACKEND_ARGS

        :return:
        """
        _logger().debug('restart backend with interpreter %s' %
                        self.BACKEND_INTERPRETER)
        self.backend.stop()
        if os.path.exists(_get_backend_libs_path()):
            args = self.BACKEND_ARGS
        else:
            args = []
        _logger().debug('backend args %r' % args)
        self.backend.start(
            self.BACKEND_SERVER, self.BACKEND_INTERPRETER, args)

    def close(self, *args):
        self.line_highlighter = None
        self.breakpoints_panel = None
        super().close(*args)

    def clone(self):
        clone = self.__class__(
            parent=self.parent(),
            color_scheme=self.syntax_highlighter.color_scheme.name)
        clone.restart_backend()
        return clone

    def __repr__(self):
        return 'PyCodeEdit(path=%r)' % self.file.path


class PyCodeEditorPlugin(plugins.EditorPlugin):
    @staticmethod
    def get_editor_class():
        PyCodeEdit.BACKEND_ARGS = [
            '-s', _get_backend_libs_path()]
        return PyCodeEdit

    @staticmethod
    def get_specific_preferences_page():
        return PythonEditorPreferences()

    @staticmethod
    def apply_specific_preferences(editor):
        """
        Apply preferences specific to the python editor.

        :param editor: Editor instance to configure
        :type editor: PyCodeEdit
        """
        editor.file.fold_docstrings = get_fold_docstrings()
        editor.file.fold_imports = get_fold_imports()

        try:
            if api.utils.is_dark_color_scheme(api.utils.color_scheme()):
                editor.line_highlighter.background = QtGui.QColor('#2D6099')
                editor.breakpoints_panel.background = QtGui.QColor('#3A2323')
            else:
                editor.line_highlighter.background = QtGui.QColor('#6DC0F9')
                editor.breakpoints_panel.background = QtGui.QColor('#FFC8C8')
        except AttributeError as e:
            _logger().warn(str(e))

        try:
            m = editor.modes.get('CommentsMode')
        except KeyError:
            _logger().warn('editor %r has no CommentsMode', editor)
        else:
            m.action.setShortcut(api.shortcuts.get(
                'Comment/Uncomment', _('Comment/Uncomment'), 'Ctrl+/'))

        try:
            m = editor.modes.get('GoToAssignmentsMode')
        except KeyError:
            _logger().warn('editor %r has no GoToAssignmentsMode', editor)
        else:
            m.action_goto.setShortcut(api.shortcuts.get(
                'Goto assignments', _('Goto assignments'), 'F7'))

        try:
            m = editor.panels.get('QuickDocPanel')
        except KeyError:
            _logger().warn('editor %r has no QuickDocPanel', editor)
        else:
            m.action_quick_doc.setShortcut(api.shortcuts.get(
                'Show documentation', _('Show documentation'), 'Alt+Q'))


class PyCodeEditorIntegration(plugins.WorkspacePlugin):
    def activate(self):
        plugins.WorkspacePlugin.__init__(self, self.main_window)
        self.main_window.editor_loaded.connect(self._on_tab_created)
        self.main_window.about_to_open_tab.connect(self._set_backend_options)

    def _on_tab_created(self, tab):
        if isinstance(tab, PyCodeEdit):
            try:
                mode = tab.modes.get('GoToAssignmentsMode')
            except KeyError:
                _logger().warn('editor %r has no GoToAssignmentsMode', tab)
            else:
                mode.out_of_doc.connect(self._on_goto_other_file)
            tab.restart_backend()

    @staticmethod
    def _on_goto_other_file(assignment):
        path = assignment.module_path
        line = assignment.line
        column = assignment.column
        api.editor.open_file(path, line, column)

    @staticmethod
    def _set_backend_options(*args):
        # this is needed only for python, to know which interpreter to
        # use for the backend, if interpreter is different than
        # sys.executable, it will use backend-libraries stored in
        # app data (so that users don't have to install pyqode libs into
        # their target env)
        from .interpreters import PythonManager
        PyCodeEdit.BACKEND_INTERPRETER = PythonManager(
            ).get_project_interpreter(api.project.get_current_project())
        _logger().debug(
            'backend interpreter: %s' % PyCodeEdit.BACKEND_INTERPRETER)


def get_fold_docstrings():
    return bool(int(QtCore.QSettings().value(
        'python/fold_docstrings', 0)))


def set_fold_docstrings(value):
    return QtCore.QSettings().setValue(
        'python/fold_docstrings', int(value))


def get_fold_imports():
    return bool(int(QtCore.QSettings().value(
        'python/fold_imports', 0)))


def set_fold_imports(value):
    return QtCore.QSettings().setValue(
        'python/fold_imports', int(value))


class PythonEditorPreferences(api.widgets.PreferencePage):
    def __init__(self):
        super().__init__(
            'Python', icon=api.widgets.FileIconProvider.mimetype_icon(
                'file.py'))
        self.ui = settings_page_editor_ui.Ui_Form()
        self.ui.setupUi(self)

    def reset(self):
        self.ui.cb_fold_docstrings.setChecked(get_fold_docstrings())
        self.ui.cb_fold_imports.setChecked(get_fold_imports())

    @staticmethod
    def restore_defaults():
        set_fold_docstrings(False)
        set_fold_imports(False)

    def save(self):
        set_fold_docstrings(self.ui.cb_fold_docstrings.isChecked())
        set_fold_imports(self.ui.cb_fold_imports.isChecked())
