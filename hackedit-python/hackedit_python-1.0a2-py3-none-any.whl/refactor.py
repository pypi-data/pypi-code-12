import logging
import os
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from hackedit import api
from hackedit.api import special_icons, plugins
from hackedit.api.widgets import DiffViewer, FindResultsWidget
from pyqode.core.api import TextHelper
from rope.base import libutils, worder
from rope.base.exceptions import RopeError
from rope.base.fscommands import FileSystemCommands
from rope.base.project import Project, NoProject
from rope.contrib.findit import find_occurrences
from rope.refactor import multiproject
from rope.refactor.extract import ExtractMethod, ExtractVariable
from rope.refactor.importutils import ImportOrganizer
from rope.refactor.rename import Rename

from hackedit_python.editor import PyCodeEdit
from hackedit_python.forms import dlg_rope_rename_ui


_ = api.gettext.get_translation(package='hackedit-python')


def _logger():
    return logging.getLogger(__name__)


class RefactoringErrorEvent(api.events.ExceptionEvent):
    def __init__(self, error):
        if error.critical:
            title = _('Rope error')
            description = (_('An error occured during refactoring...\n'
                             'Exception: "%s"\n') % error.exc)
        else:
            title = _('Refactoring failed')
            description = _('Reason: "%s"') % error.exc
        super().__init__(title, description, error.exc, tb=error.traceback)
        if not error.critical:
            self.level = api.events.WARNING
            self.custom_actions.remove(self.action_report)


class PyRefactor(plugins.WorkspacePlugin):
    """
    Adds some refactoring capabilities to the IDE (using the rope library).

    Supported operations:
        - Rename
        - Extract method
        - Extract variable
        - Find occurrences
        - Organize imports

    """
    def activate(self):
        self._preview_dock = None
        self._occurrences_dock = None
        self._occurrences_results = None
        self._review_widget = None
        api.signals.connect_slot(api.signals.CURRENT_PROJECT_CHANGED,
                                 self._on_current_project_changed)
        api.signals.connect_slot(api.signals.EDITOR_CREATED,
                                 self._on_editor_created)
        api.signals.connect_slot(api.signals.CURRENT_EDITOR_CHANGED,
                                 self._update_edit_actions_state)
        path = api.project.get_current_project()
        self._main_project = Project(path, ropefolder=api.project.FOLDER,
                                     fscommands=FileSystemCommands())
        self._main_project.validate()
        api.signals.connect_slot(api.signals.DOCUMENT_SAVED,
                                 self._on_document_saved)

    def close(self):
        self._main_project.close()

    def rename(self):
        """
        Renames word under cursor.
        """
        editor = api.editor.get_current_editor()
        if editor is None:
            return
        editor.file.save()
        assert isinstance(editor, PyCodeEdit)
        module = libutils.path_to_resource(
            self._main_project, editor.file.path)
        self._main_project.validate()
        cursor_position = self._get_real_position(
            editor.textCursor().position())
        try:
            renamer = Rename(self._main_project, module, cursor_position)
        except RopeError:
            return
        if not renamer.get_old_name():
            return
        preview, replacement = DlgRope.rename(
            self.main_window, renamer.get_old_name())
        if preview is None and replacement is None:
            return
        multiproj = self._has_multiple_projects()
        other_projects = self._get_other_projects()
        main_project = self._main_project
        self._preview = preview
        api.tasks.start(_('Refactoring: rename'), rename_symbol,
                        self._on_changes_available,
                        args=(
                            main_project, multiproj, other_projects,
                            editor.file.path, cursor_position, replacement),
                        cancellable=True, use_thread=True)

    def organise_imports(self):
        editor = api.editor.get_current_editor()
        api.editor.save_all_editors()
        if editor is None:
            return
        self._preview = True
        file_path = editor.file.path
        project = self.get_project_for_file(file_path)
        if project:
            api.tasks.start(
                _('Refactoring: organize imports'), organize_imports,
                self._on_changes_available,
                args=(project, file_path),
                cancellable=True, use_thread=True)

    def extract_method(self):
        """
        Extracts a method from the selected text (if possible, otherwise a
        warning message will appear).
        """
        api.editor.save_all_editors()
        self._main_project.validate()
        editor = api.editor.get_current_editor()
        if editor is None or not editor.textCursor().hasSelection():
            return
        editor.file.save()
        if not editor.textCursor().hasSelection():
            TextHelper(editor).select_whole_line()
        start = self._get_real_position(editor.textCursor().selectionStart())
        end = self._get_real_position(editor.textCursor().selectionEnd())
        preview, replacement = DlgRope.extract_method(self.main_window)
        if preview is None and replacement is None:
            return
        multiproj = self._has_multiple_projects()
        other_projects = self._get_other_projects()
        main_project = self._main_project
        cursor_position_start = start
        cursor_position_end = end
        replacement = replacement
        self._preview = preview
        api.tasks.start(
            _('Refactoring: extract method'), extract_method,
            self._on_changes_available,
            args=(multiproj, main_project, other_projects, editor.file.path,
                  cursor_position_start, cursor_position_end, replacement),
            cancellable=True, use_thread=True)

    def extract_variable(self):
        """
        Extracts a variable from the selected statement (if possible).
        """
        api.editor.save_all_editors()
        self._main_project.validate()
        editor = api.editor.get_current_editor()
        if editor is None or not editor.textCursor().hasSelection():
            return
        editor.file.save()
        if not editor.textCursor().hasSelection():
            TextHelper(editor).select_whole_line()
        start = self._get_real_position(editor.textCursor().selectionStart())
        end = self._get_real_position(editor.textCursor().selectionEnd())
        preview, replacement = DlgRope.extract_variable(self.main_window)
        if preview is None and replacement is None:
            return
        multiproj = self._has_multiple_projects()
        other_projects = self._get_other_projects()
        main_project = self._main_project
        cursor_position_start = start
        cursor_position_end = end
        replacement = replacement
        self._preview = preview
        api.tasks.start(
            _('Refactoring: extract variable'), extract_variable,
            self._on_changes_available,
            args=(multiproj, main_project, other_projects, editor.file.path,
                  cursor_position_start, cursor_position_end, replacement),
            cancellable=True, use_thread=True)

    def find_usages(self):
        """
        Find all usages of the word under cursor.
        """
        api.editor.save_all_editors()
        if api.editor.get_current_editor() is None:
            return
        file_path = api.editor.get_current_path()
        api.editor.save_current_editor()
        offset = self._get_real_position(
            api.editor.get_current_editor().textCursor().position())
        self._occurrence_to_search = worder.get_name_at(
            libutils.path_to_resource(self._main_project, file_path), offset)
        main_project = api.project.get_current_project()
        other_projects = self._get_other_projects(path_only=True)
        file_path = file_path
        api.tasks.start(
            _('Refactoring: find usages'), find_usages,
            self._on_find_usages_finished,
            args=(main_project, other_projects, file_path, offset),
            cancellable=True, use_thread=True)

    def get_project_for_file(self, path):
        for prj in [self._main_project] + self._get_other_projects():
            p = prj.address + os.path.sep
            if p in path:
                return prj
        return None

    @staticmethod
    def clean_changes(pending_changes):
        if hasattr(pending_changes, '__iter__'):
            cleaned = []
            for prj, changeset in pending_changes:
                for change in changeset.changes:
                    if isinstance(change.resource.project, NoProject):
                        break
                else:
                    cleaned.append((prj, changeset))
            return cleaned
        return pending_changes

    def _on_changes_available(self, changes):
        if isinstance(changes, RefactoringError):
            api.events.post(RefactoringErrorEvent(changes), False)
            return
        _, self._pending_changes = changes

        self._pending_changes = self.clean_changes(self._pending_changes)

        if self._pending_changes is None:
            return
        if self._preview and self._pending_changes:
            self._create_review_dock()
            self._update_preview()
        else:
            self._refactor()

    def _on_find_usages_finished(self, results):
        if results is None:
            # todo: show no results notification
            return
        if isinstance(results, RefactoringError):
            api.events.post(RefactoringErrorEvent(results), False)
            return
        if self._occurrences_results is None:
            self._create_occurrences_dock()
        else:
            self._occurrences_dock.show()
            self._occurrences_dock.button.show()
            self._occurrences_dock.button.action.setVisible(True)
        self._occurrences_results.show_results(
            results, self._occurrence_to_search)

    @staticmethod
    def apply_preferences():
        for editor in api.editor.get_all_editors(True):
            if isinstance(editor, PyCodeEdit):
                actions = editor.refactoring_actions
                items = [
                    ('usages', 'Find usages', _('Find usages'), 'Alt+F7'),
                    ('rename', 'Refactor: rename', _('Refactor: rename'),
                     'Shift+F6'),
                    ('extract_method', 'Refactor: extract method',
                     _('Refactor: extract method'), 'Ctrl+Alt+M'),
                    ('extract_var', 'Refactor: extract variable',
                     _('Refactor: extract variable'), 'Ctrl+Alt+V'),
                    ('imports', 'Refactor: organize imports',
                     _('Refactor: organize imports'), 'Alt+F8')
                ]
                for id, name, text, default in items:
                    actions[id].setShortcut(api.shortcuts.get(
                        name, text, default))

                actions['extract_var'].setIcon(special_icons.variable_icon())

    def create_refactor_menu(self, editor):
        """
        Creates the refactor menu; this menu will appear in the menu bar of the
        main window and in the context menu of any python editor.
        """
        mnu_refactor = QtWidgets.QMenu(editor)
        mnu_refactor.setTitle(_('Refactor'))
        mnu_refactor.setIcon(QtGui.QIcon.fromTheme('edit-rename'))

        action_find_usages = mnu_refactor.addAction(_('Find usages'))
        action_find_usages.setToolTip(
            _('Find occurrences of symbol under cursor'))
        action_find_usages.setIcon(QtGui.QIcon.fromTheme('edit-find'))
        action_find_usages.setShortcut(
            api.shortcuts.get('Find usages', _('Find usages'), 'Alt+F7'))
        action_find_usages.triggered.connect(self.find_usages)

        # Rename
        action_rename = mnu_refactor.addAction(_('Rename'))
        action_rename.setToolTip(_('Rename symnbol under cursor'))
        action_rename.setIcon(QtGui.QIcon.fromTheme('edit-find-replace'))
        action_rename.setShortcut(
            api.shortcuts.get('Refactor: rename', _('Refactor: rename'),
                              'Shift+F6'))
        action_rename.triggered.connect(self.rename)

        # Extract variable
        action_extract_var = mnu_refactor.addAction(_('Extract variable'))
        action_extract_var.setToolTip(
            _('Extract variable (a statement must be selected)'))
        action_extract_var.setIcon(special_icons.variable_icon())
        action_extract_var.setShortcut(
            api.shortcuts.get('Refactor: extract variable',
                              _('Refactor: extract variable'), 'Ctrl+Alt+V'))
        action_extract_var.triggered.connect(self.extract_variable)

        # Extract method
        action_extract_method = mnu_refactor.addAction(_('Extract method'))
        action_extract_method.setToolTip(
            _('Extract method (some statements must be selected)'))
        action_extract_method.setIcon(special_icons.function_icon())
        action_extract_method.setShortcut(
            api.shortcuts.get('Refactor: extract method',
                              _('Refactor: extract method'), 'Ctrl+Alt+M'))
        action_extract_method.triggered.connect(self.extract_method)

        mnu_refactor.addSeparator()

        action_organize_imports = mnu_refactor.addAction(_('Organize imports'))
        action_organize_imports.setToolTip(
            _('Organize top level imports (sort, remove unused,...)'))
        action_organize_imports.setIcon(special_icons.namespace_icon())
        action_organize_imports.setShortcut(
            api.shortcuts.get('Refactor: organize imports',
                              _('Refactor: organize imports'), 'Alt+F8'))
        action_organize_imports.triggered.connect(self.organise_imports)

        actions = {
            'usages': action_find_usages,
            'rename': action_rename,
            'extract_method': action_extract_method,
            'extract_var': action_extract_var,
            'imports': action_organize_imports
        }

        return mnu_refactor, actions

    def _on_current_project_changed(self, path):
        """
        Changes the active rope project when the current project changed in
        the IDE.
        :param path: Path of the new project.
        """
        self._main_project.close()
        self._main_project = Project(path, ropefolder=api.project.FOLDER,
                                     fscommands=FileSystemCommands())
        self._main_project.validate()

    def _on_editor_created(self, editor):
        """
        Adds the refactor menu to the editor that have just been created.
        :param editor: editor to modify.
        """
        if isinstance(editor, PyCodeEdit):
            sep = QtWidgets.QAction(editor)
            sep.setSeparator(True)
            menu, actions = self.create_refactor_menu(editor)
            editor.insert_action(menu.menuAction(), 0)
            editor.refactoring_actions = actions
            editor.insert_action(sep, 1)
            editor.cursorPositionChanged.connect(
                self._update_edit_actions_state)

    @staticmethod
    def _update_edit_actions_state(editor=None):
        if editor is None:
            editor = api.editor.get_current_editor()
        if isinstance(editor, PyCodeEdit):
            flg = bool(TextHelper(editor).word_under_cursor(
                select_whole_word=True).selectedText())
            try:
                editor.refactoring_actions
            except AttributeError:
                return
            else:
                editor.refactoring_actions['usages'].setEnabled(flg)
                editor.refactoring_actions['rename'].setEnabled(flg)
                flg = editor.textCursor().hasSelection()
                editor.refactoring_actions['extract_method'].setEnabled(flg)
                editor.refactoring_actions['extract_var'].setEnabled(flg)

    def _create_occurrences_dock(self):
        """
        Creates the dock widget that shows all the occurrences of a python
        name.
        """
        self._occurrences_widget = QtWidgets.QWidget()
        vlayout = QtWidgets.QVBoxLayout()
        # buttons
        self._setup_occurrences_buttons(vlayout)
        self._occurrences_results = FindResultsWidget(term='usages')
        self._occurrences_results.itemActivated.connect(
            self._on_occurrence_activated)
        vlayout.addWidget(self._occurrences_results)
        self._occurrences_widget.setLayout(vlayout)
        # Dock widget
        self._occurrences_dock = api.window.add_dock_widget(
            self._occurrences_widget, _('Find usages'),
            QtGui.QIcon.fromTheme('edit-find'),
            QtCore.Qt.BottomDockWidgetArea)

    @staticmethod
    def _on_occurrence_activated(item):
        assert isinstance(item, QtWidgets.QTreeWidgetItem)
        data = item.data(0, QtCore.Qt.UserRole)
        try:
            l = data['line']
        except TypeError:
            return  # file item or root item
        l = data['line']
        start = data['start']
        lenght = data['end'] - start
        if data is not None:
            # open editor and go to line/column
            editor = api.editor.open_file(
                data['path'], data['line'], data['start'])
            if editor is None:
                return
            # select text
            helper = TextHelper(editor)
            cursor = helper.select_lines(start=l, end=l)
            cursor.movePosition(cursor.StartOfBlock)
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, start)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, lenght)
            editor.setTextCursor(cursor)

    def _setup_occurrences_buttons(self, vlayout):
        """
        Creates the occurrences dock widget buttons
        :param vlayout: main layout
        """
        buttons = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        # Close
        bt = QtWidgets.QPushButton()
        bt.setText(_('Close'))
        bt.clicked.connect(self._remove_occurrences_dock)
        buttons_layout.addWidget(bt)
        # Spacer
        buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding))
        buttons.setLayout(buttons_layout)
        vlayout.addWidget(buttons)

    def _create_review_dock(self):
        """
        Creates the dock widget that shows the refactor diff.
        """
        if self._review_widget:
            self._preview_dock.show()
            self._preview_dock.button.show()
            self._preview_dock.button.action.setVisible(True)
            return
        self._review_widget = QtWidgets.QWidget()
        vlayout = QtWidgets.QVBoxLayout()
        # buttons
        bt_refactor = self._setup_review_buttons(vlayout)
        # Diff viewer
        self._viewer = DiffViewer()
        vlayout.addWidget(self._viewer)
        self._review_widget.setLayout(vlayout)

        # Dock widget
        self._preview_dock = api.window.add_dock_widget(
            self._review_widget, _('Review'),
            QtGui.QIcon.fromTheme('edit-find'),
            QtCore.Qt.BottomDockWidgetArea)
        bt_refactor.setFocus()

    def _update_preview(self):
        try:
            texts = []
            for prj, changes in self._pending_changes:
                lines = ''
                for subchanges in changes.changes:
                    resource = subchanges.get_changed_resources()[0]
                    resource_path = resource.real_path
                    if prj.address + os.sep in resource_path:
                        desc = subchanges.get_description()
                        lines += desc
                if lines:
                    texts.append('%s\n\n*** Project: %s\n\n%s\n' %
                                 (str(changes), prj.address, lines))
            self._viewer.setPlainText('\n'.join(texts))
        except TypeError:
            # not multiproj, one single change set
            self._viewer.setPlainText(self._pending_changes.get_description())

    def _setup_review_buttons(self, vlayout):
        """
        Creates the buttons of the preview dock widget
        :param vlayout: main layout
        """
        buttons = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        bt_refactor = bt = QtWidgets.QPushButton()
        bt.setText(_('Refactor'))
        bt.clicked.connect(self._refactor)
        buttons_layout.addWidget(bt)
        # Close
        bt = QtWidgets.QPushButton()
        bt.setText(_('Cancel'))
        bt.clicked.connect(self._remove_preview_dock)
        buttons_layout.addWidget(bt)
        # Spacer
        buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding))
        buttons.setLayout(buttons_layout)
        vlayout.addWidget(buttons)

        return bt_refactor

    def _remove_preview_dock(self):
        """
        Removes the preview dock widget
        """
        if self._preview_dock is not None:
            self._preview_dock.hide()
            self._preview_dock.button.hide()
            self._preview_dock.button.action.setVisible(False)

    def _remove_occurrences_dock(self):
        """
        Removes the occurrences dock widget.
        """
        if self._occurrences_dock is not None:
            self._occurrences_dock.hide()
            self._occurrences_dock.button.hide()
            self._occurrences_dock.button.action.setVisible(False)

    def _refactor(self):
        """
        Performs the refactoring.
        """
        main_project = self._main_project
        multiproj = self._has_multiple_projects()
        pending_changes = self._pending_changes
        api.tasks.start(_('Refactoring: apply pending changes'),
                        apply_pending_changes, self._on_refactoring_finished,
                        args=(main_project, multiproj, pending_changes),
                        use_thread=True)

    def _on_refactoring_finished(self, ret_val):
        self._remove_preview_dock()
        if ret_val is not True:
            api.events.post(RefactoringErrorEvent(ret_val), False)

    @staticmethod
    def _get_other_projects(path_only=False):
        """
        Gets the list of secondary projects (all except current).
        """
        projects = []
        current = api.project.get_current_project()
        for path in api.project.get_projects():
            if path == current:
                continue
            if not path_only:
                prj = Project(path, ropefolder=api.project.FOLDER,
                              fscommands=FileSystemCommands())
                prj.validate()
            else:
                prj = path
            projects.append(prj)
        return projects

    @staticmethod
    def _has_multiple_projects():
        """
        Checks whether multiple project have been opened in the main window.
        :return: True if window has multiple project, False if window only has
                 one project.
        """
        return len(api.project.get_projects()) > 1

    @staticmethod
    def _on_document_saved(path, old_content):
        if not path:
            return
        project = None
        for project in api.project.get_projects():
            prj_path = project + os.sep
            if prj_path in path:
                project = Project(prj_path, ropefolder=api.project.FOLDER,
                                  fscommands=FileSystemCommands())
                break
        if project:
            if path.endswith('_rc.py'):
                return
            api.tasks.start(_('Refactoring: reporting changes'),
                            report_changes, None,
                            args=(project, path, old_content),
                            use_thread=False)

    @staticmethod
    def _get_real_position(position):
        """
        Gets the real cursor position (there might be a difference between
        editor content and file system content because of clean_trailing
        whitespaces on save). This function will converts the absolute position
        into a line/column pair and use this info to get the position in the
        file.
        """
        tc = api.editor.get_current_editor().textCursor()
        tc.setPosition(position)
        l = tc.blockNumber()
        c = tc.positionInBlock()
        e = api.editor.get_current_editor().file.encoding
        path = api.editor.get_current_editor().file.path
        try:
            with open(path, 'r', encoding=e) as f:
                lines = f.readlines()
        except OSError:
            _logger().exception('failed to read file %s', path)
            lines = []
        real_pos = 0
        for i, line in enumerate(lines):
            if i == l:
                real_pos += c
                break
            else:
                real_pos += len(line)
        return real_pos


class DlgRope(QtWidgets.QDialog):
    """
    Asks the user for some text input and let them choose whether to perform
    the refactoring directly or to preview the changes first.
    """
    def __init__(self, parent, symbol_under_cursor):
        super().__init__(parent)
        self._symbol_under_cursor = symbol_under_cursor
        self.preview_changes = False
        self.ui = dlg_rope_rename_ui.Ui_Dialog()
        self.ui.setupUi(self)
        text = self.ui.label.text() % symbol_under_cursor
        self.ui.label.setText(text)
        self.ui.buttonBox.button(self.ui.buttonBox.Apply).setText(_('Preview'))
        self.ui.buttonBox.button(self.ui.buttonBox.Apply).clicked.connect(
            self._preview)
        self.ui.buttonBox.button(self.ui.buttonBox.Ok).setText(_('Refactor'))
        self.ui.lineEdit.selectAll()
        self.ui.lineEdit.setFocus()
        self.ui.lineEdit.textChanged.connect(self._on_text_changed)
        self.ui.lineEdit.setText(symbol_under_cursor)

    def _preview(self):
        self.preview_changes = True
        self.accept()

    def _on_text_changed(self, text):
        self.ui.buttonBox.button(self.ui.buttonBox.Apply).setEnabled(
            text not in ['', self._symbol_under_cursor])
        self.ui.buttonBox.button(self.ui.buttonBox.Ok).setEnabled(
            text not in ['', self._symbol_under_cursor])

    @classmethod
    def rename(cls, parent, symbol_under_cursor):
        """
        Shows dialog for the Rename operation.

        :param parent: Parent widget
        :param symbol_under_cursor: Word under text cursor of the active editor
        :return: preview_flag, refactoring_diff (or None, None if the dialog
                 has been canceled by the user).
        """
        dlg = cls(parent, symbol_under_cursor)
        dlg.setWindowTitle(_('Rename'))
        if dlg.exec_() == dlg.Accepted:
            return dlg.preview_changes, dlg.ui.lineEdit.text()
        return None, None

    @classmethod
    def extract_method(cls, parent):
        """
        Shows dialog for the extract method operation.

        :param parent: Parent widget
        :return: preview_flag, refactoring_diff (or None, None if the dialog
                 has been canceled by the user).
        """
        dlg = cls(parent, '')
        dlg.setWindowTitle(_('Extract method'))
        dlg.ui.label.hide()
        if dlg.exec_() == dlg.Accepted:
            return dlg.preview_changes, dlg.ui.lineEdit.text()
        return None, None

    @classmethod
    def extract_variable(cls, parent):
        """
        Shows dialog for the extract variable operation.

        :param parent: Parent widget
        :return: preview_flag, refactoring_diff (or None, None if the dialog
                 has been canceled by the user).
        """
        dlg = cls(parent, '')
        dlg.setWindowTitle(_('Extract variable'))
        dlg.ui.label.hide()
        if dlg.exec_() == dlg.Accepted:
            return dlg.preview_changes, dlg.ui.lineEdit.text()
        return None, None


class RefactoringError(Exception):
    pass


# ---------  Background process methods
def apply_pending_changes(_, main_project, multiproj, pending_changes):
    """
    Apply pending changes.
    """
    try:
        main_project.validate()
        pending_changes = pending_changes
        if multiproj:
            try:
                multiproject.perform(pending_changes)
            except TypeError:
                main_project.do(pending_changes)
        else:
            main_project.do(pending_changes)
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error
    else:
        return True


def rename_symbol(_, main_project, multiproj, other_projects, file_path,
                  cursor_position, replacement):
    """
    Renames symbol under cusror.
    """
    try:
        main_project.validate()
        module = libutils.path_to_resource(main_project, file_path)
        if multiproj:
            # we need to rename cross project
            crossrename = multiproject.MultiProjectRefactoring(
                Rename, other_projects)
            renamer = crossrename(main_project, module, cursor_position)
            pending_changes = renamer.get_all_changes(replacement, docs=True)
        else:
            renamer = Rename(main_project, module, cursor_position)
            pending_changes = renamer.get_changes(replacement, docs=True)
        return multiproj, pending_changes
    except RopeError as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = False
        return error
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error


def extract_method(_, multiproj, main_project, other_projects, file_path,
                   cursor_position_start, cursor_position_end, replacement):
    """
    Extract method from selection
    """
    try:
        main_project.validate()
        module = libutils.path_to_resource(main_project, file_path)
        if multiproj:
            # we need to rename cross project
            crossrename = multiproject.MultiProjectRefactoring(
                ExtractMethod, other_projects)
            extractor = crossrename(
                main_project, module, cursor_position_start,
                cursor_position_end)
            pending_changes = extractor.get_all_changes(replacement)
        else:
            extractor = ExtractMethod(
                main_project, module, cursor_position_start,
                cursor_position_end)
            pending_changes = extractor.get_changes(replacement, similar=True)
        return multiproj, pending_changes
    except RopeError as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = False
        return error
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error


def extract_variable(_, multiproj, main_project, other_projects, file_path,
                     cursor_position_start, cursor_position_end, replacement):
    """
    Extract variable from selection
    """
    try:
        main_project.validate()
        module = libutils.path_to_resource(main_project, file_path)
        if multiproj:
            # we need to rename cross project
            crossrename = multiproject.MultiProjectRefactoring(
                ExtractVariable, other_projects)
            extractor = crossrename(
                main_project, module, cursor_position_start,
                cursor_position_end)
            pending_changes = extractor.get_all_changes(replacement)
        else:
            extractor = ExtractVariable(
                main_project, module, cursor_position_start,
                cursor_position_end)
            pending_changes = extractor.get_changes(replacement, similar=True)
        return multiproj, pending_changes
    except RopeError as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = False
        return error
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error


def find_usages(_, main_project, other_projects, file_path, offset):
    """
    Find usages of symbol under cursor.
    """
    try:
        occurrences = []
        if other_projects:
            for path in [main_project] + other_projects:
                prj = Project(path, ropefolder=api.project.FOLDER,
                              fscommands=FileSystemCommands())
                prj.validate()
                mod = libutils.path_to_resource(prj, file_path)
                occurrences += find_occurrences(
                    prj, mod, offset, unsure=False, in_hierarchy=True)
                prj.close()
        else:
            prj = Project(main_project, ropefolder=api.project.FOLDER,
                          fscommands=FileSystemCommands())
            prj.validate()
            mod = libutils.path_to_resource(prj, file_path)
            occurrences = find_occurrences(prj, mod, offset, unsure=False,
                                           in_hierarchy=True)
        # transform results to a serialisable list of usages that is ready
        # to use by the find_results widget.
        occurrences_map = {}
        for location in occurrences:
            path = location.resource.real_path
            lineno = location.lineno - 1
            # convert file region to line region
            content = location.resource.read()
            offset = location.offset
            char = content[offset]
            while char != '\n':  # find start of line
                offset -= 1
                char = content[offset]
            # update offsets
            start = location.offset - offset - 1
            end = location.region[1] - offset - 1
            line_text = content.splitlines()[lineno]
            data = (lineno, line_text, [(start, end)])
            if path not in occurrences_map:
                occurrences_map[path] = [data]
            else:
                occurrences_map[path].append(data)
        results = []
        for key, value in occurrences_map.items():
            results.append((key, value))
        results = sorted(results, key=lambda x: x[0])
        return results
    except RopeError as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = False
        return error
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error


def organize_imports(_, project, file_path):
    try:
        project.validate()
        module = libutils.path_to_resource(project, file_path)
        organizer = ImportOrganizer(project)
        pending_changes = organizer.organize_imports(module)
        return False, pending_changes
    except RopeError as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = False
        return error
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error


def report_changes(_, project, path, old_content):
    try:
        try:
            libutils.report_change(project, path, old_content)
        except AttributeError:
            _logger().warn('failed to report change for file %r, file outside '
                           'of the project root dir?', path)
    except RopeError as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = False
        return error
    except Exception as e:
        error = RefactoringError()
        error.exc = str(e)
        error.traceback = traceback.format_exc()
        error.critical = True
        return error
