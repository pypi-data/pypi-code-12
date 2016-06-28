import json
import logging
import os
import time
from fnmatch import fnmatch

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqode.core.cache import Cache
from pyqode.core.api import TextHelper
from pyqode.core.backend.workers import findall

from hackedit import api
from hackedit.api import editor, plugins, shortcuts, window
from hackedit.api.utils import is_ignored_path
from hackedit.api.widgets import FindResultsWidget
from hackedit.app import settings
from hackedit.app.forms.dlg_find_replace_ui import Ui_Dialog


# Try to use the new scandir function, introduced in python 3.5
# also available from the scandir package on pypi
try:
    # new scandir function in python 3.5
    from os import scandir as listdir
except ImportError:
    try:
        # new scandir function from scandir package on pypi
        from scandir import scandir as listdir
    except ImportError:
        # scandir function not found, use the slow listdir function
        from os import listdir


class FindReplace(plugins.WorkspacePlugin):
    """
    This plugin lets you find (and replace) some text in a series
    of files (usually project files).
    """
    def activate(self):
        self._dock = None
        self._find_results_widget = None
        self._replace = False
        mnu_edit = window.get_menu(_('&Edit'))
        action_before = mnu_edit.actions()[-1]
        sep = QtWidgets.QAction(mnu_edit)
        sep.setSeparator(True)
        mnu_edit.insertAction(action_before, sep)

        # find
        self.afind = QtWidgets.QAction(mnu_edit)
        self.afind.setText(_('Find in path'))
        self.afind.setToolTip(_('Find in path'))
        self.afind.setIcon(QtGui.QIcon.fromTheme('edit-find'))
        self.afind.setShortcut(shortcuts.get(
            'Find in path', _('Find in path'), 'Ctrl+Shift+F'))
        self.afind.triggered.connect(self._on_find_triggered)
        mnu_edit.insertAction(action_before, self.afind)

        # replace
        self.areplace = QtWidgets.QAction(mnu_edit)
        self.areplace.setIcon(QtGui.QIcon.fromTheme('edit-find-replace'))
        self.areplace.setText(_('Replace in path'))
        self.areplace.setToolTip(_('Replace in path'))
        self.areplace.setShortcut(shortcuts.get(
            'Replace in path', _('Replace in path'), 'Ctrl+Shift+H'))
        self.areplace.triggered.connect(self._on_replace_triggered)
        mnu_edit.insertAction(action_before, self.areplace)

        sep = QtWidgets.QAction(mnu_edit)
        sep.setSeparator(True)
        mnu_edit.insertAction(action_before, sep)

        api.window.add_actions(mnu_edit.actions())

    def apply_preferences(self):
        self.areplace.setShortcut(shortcuts.get(
            'Replace in path', _('Replace in path'), 'Ctrl+Shift+H'))
        self.afind.setShortcut(shortcuts.get(
            'Find in path', _('Find in path'), 'Ctrl+Shift+F'))

    def _create_dock(self):
        self._find_widget = QtWidgets.QWidget()
        vlayout = QtWidgets.QVBoxLayout()

        # buttons
        buttons = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        # Search again
        bt = QtWidgets.QPushButton()
        bt.setText(_('Search again'))
        bt.clicked.connect(self._search_again)
        buttons_layout.addWidget(bt)
        if self._replace:
            # Replace
            bt = QtWidgets.QPushButton()
            bt.setText(_('Replace all'))
            bt.clicked.connect(self._replace_all)
            buttons_layout.addWidget(bt)
            # Replace selected
            bt = QtWidgets.QPushButton()
            bt.clicked.connect(self._replace_selected)
            buttons_layout.addWidget(bt)
        # Close
        bt = QtWidgets.QPushButton()
        bt.setText(_('Close'))
        bt.clicked.connect(self._remove_dock)
        buttons_layout.addWidget(bt)
        # Spacer
        buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding))
        buttons.setLayout(buttons_layout)
        vlayout.addWidget(buttons)

        # Find widget
        self._find_results_widget = FindResultsWidget()
        vlayout.addWidget(self._find_results_widget)
        self._find_widget.setLayout(vlayout)

        # Dock widget
        self._dock = window.add_dock_widget(
            self._find_widget, _('Find'), QtGui.QIcon.fromTheme('edit-find'),
            QtCore.Qt.BottomDockWidgetArea)
        self._find_results_widget.itemActivated.connect(
            self._on_item_activated)

    def _search_again(self):
        self._find_results_widget.clear()
        self._start_search_in_path(self._search_settings)

    def _remove_dock(self):
        if self._dock is not None:
            window.remove_dock_widget(self._dock)
            self._dock.close()
            self._dock.deleteLater()
            self._dock = None

    @staticmethod
    def _on_item_activated(item, *args):
        assert isinstance(item, QtWidgets.QTreeWidgetItem)
        data = item.data(0, QtCore.Qt.UserRole)
        try:
            l = data['line']
        except TypeError:
            return  # file item or root item
        start = data['start']
        lenght = data['end'] - start
        if data is not None:
            # open editor and go to line/column
            e = editor.open_file(data['path'], data['line'], data['start'])
            if e is None:
                return
            # select text
            helper = TextHelper(e)
            try:
                cursor = helper.select_lines(start=l, end=l)
            except AttributeError:
                _logger().debug('failed to select occurent line in editor, not'
                                ' a subclass of QPlainTextEdit')
            else:
                assert isinstance(cursor, QtGui.QTextCursor)
                cursor.movePosition(cursor.StartOfBlock)
                cursor.movePosition(cursor.Right, cursor.MoveAnchor, start)
                cursor.movePosition(cursor.Right, cursor.KeepAnchor, lenght)
                e.setTextCursor(cursor)

    def _on_find_triggered(self):
        text = ''
        if editor.get_current_editor() is not None:
            try:
                text = TextHelper(editor.get_current_editor()).selected_text()
            except AttributeError:
                text = ''
        search_settings = _DlgFindReplace.find(
            self.main_window, text_to_find=text)
        if search_settings is not None:
            self._remove_dock()
            self._replace = False
            self._start_search_in_path(search_settings)

    def _start_search_in_path(self, search_settings):
        self._search_settings = search_settings
        callback = self._on_search_finished
        api.tasks.start(
            _('searching for %r') % search_settings['find'],
            search_in_path, callback,
            args=(search_settings, ))

    def _on_replace_triggered(self):
        text = ''
        if editor.get_current_editor() is not None:
            text = TextHelper(editor.get_current_editor()).selected_text()
        search_settings = _DlgFindReplace.replace(
            self.main_window, text_to_find=text)
        if search_settings is not None:
            self._remove_dock()
            self._replace = True
            self._start_search_in_path(search_settings)

    def _on_search_finished(self, results):
        if results is None:
            self._remove_dock()
            return
        if self._dock is None:
            self._create_dock()
        else:
            self._dock.show()
            self._dock.button.show()
            self._dock.button.action.setVisible(True)
        self._dock.show()
        self._find_results_widget.show_results(
            results, self._search_settings['find'])

    def _get_delta(self):
        search_term = self._search_settings['find']
        replacement = self._search_settings['replace']
        return len(replacement) - len(search_term)

    def _replace_all(self):
        delta = self._get_delta()
        replacement = self._search_settings['replace']
        data_list = self._find_results_widget.data_list
        cpy = data_list.copy()
        for data in cpy:
            try:
                with open(data['path'], 'r') as fin:
                    content = fin.read()
                    newlines = fin.newlines
            except OSError:
                continue
            lines = content.splitlines()
            line = lines[data['line']]
            assert isinstance(line, str)
            line = line[:data['start']] + replacement + line[data['end']:]
            lines[data['line']] = line
            try:
                with open(data['path'], 'w') as fout:
                    fout.write(newlines.join(lines) + newlines)
            except OSError:
                continue
            data_list.remove(data)

            # update occurrences that are on the same line, in the same file
            for next_data in data_list:
                if next_data['path'] == data['path'] and \
                        next_data['line'] == data['line']:
                    next_data['start'] += delta
                    next_data['end'] += delta
                else:
                    break
        self._remove_dock()

    def _replace_selected(self):
        item = self._find_results_widget.selectedItems()[0]
        data = item.data(0, QtCore.Qt.UserRole)
        if data is None:
            item.setSelected(False)
            return
        line = data['line']
        replacement = self._search_settings['replace']
        delta = self._get_delta()
        # open editor and select text to replace
        self._on_item_activated(item, 0)
        e = editor.get_current_editor()
        cursor = e.textCursor()
        cursor.removeSelectedText()
        cursor.insertText(replacement)
        e.setTextCursor(cursor)

        # remove
        file_item = item.parent()
        assert isinstance(file_item, QtWidgets.QTreeWidgetItem)  # for jedi
        root = self._find_results_widget.topLevelItem(0)
        next_child = None
        file_item.removeChild(item)
        if file_item.childCount():
            # update occurrences position that are on the line we just modified
            for i in range(file_item.childCount()):
                child = file_item.child(i)
                if next_child is None:
                    next_child = child
                assert isinstance(child, QtWidgets.QTreeWidgetItem)  # for jedi
                data = child.data(0, QtCore.Qt.UserRole)
                ch_line = data['line']
                if ch_line == line:
                    data['start'] += delta
                    data['end'] += delta
                    label = self._find_results_widget.itemWidget(child, 0)
                    label.setText(FindResultsWidget.make_display_text(
                        data['end'], ch_line, data['start'], data['text']))
                    child.setData(0, QtCore.Qt.UserRole, data)
        else:
            # remove file from results
            root.removeChild(file_item)
            next_file_item = root.child(0)
            if next_file_item is not None:
                next_child = next_file_item.child(0)
        if next_child is not None:
            self._find_results_widget.clearSelection()
            next_child.setSelected(True)
            self._find_results_widget.scrollTo(
                self._find_results_widget.indexFromItem(next_child))
            try:
                self._find_results_widget.itemActivated.emit(next_child, 0)
            except AttributeError:
                _logger().warn('failed to connect to itemActived signal, using'
                               'old version of PyQt5? (>= 5.5.2)')
        else:
            # no more results
            self._remove_dock()


def _last_search_data():
    """
    Loads the last search settings
    :return: SearchSettings dictionary
    """
    val = QtCore.QSettings().value('_cache/search_data', '')
    if val:
        return json.loads(val)
    else:
        return {
            'find': '',
            'replace': '',
            'case_sensitive': False,
            'whole_words_only': False,
            'regex': False,
            'paths': [],
            'patterns': []
        }


def _save_search_data(data):
    """
    Save the search settings
    :param data: search settings to save.
    """
    QtCore.QSettings().setValue('_cache/search_data', json.dumps(data))


def _last_search_term():
    """
    Gets the last search term
    :return:
    """
    return _last_search_data()['find']


class _DlgFindReplace(QtWidgets.QDialog):
    """
    Lets the user define the search settings
    """
    def __init__(self, parent, enable_replace, text_to_find):
        super().__init__(parent)
        self.main_window = parent
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        data = _last_search_data()
        if enable_replace:
            self.setWindowTitle(_('Find and replace'))
        else:
            self.setWindowTitle(_('Find'))
        self.ui.checkbox_case_sensitive.setChecked(data['case_sensitive'])
        self.ui.checkbox_whole_words.setChecked(data['whole_words_only'])
        self.ui.checkbox_regexp.setChecked(data['regex'])
        self.ui.edit_pattern.setText(';'.join(data['patterns']))
        self.ui.edit_find.setText(text_to_find)
        self.ui.label_replace.setVisible(enable_replace)
        self.ui.edit_replace.setVisible(enable_replace)
        self.ui.buttonBox.button(self.ui.buttonBox.Ok).setText(_('Find'))
        self.ui.combo_projects.addItems(parent.projects)
        self.ui.edit_find.selectAll()

    def _on_bt_dir_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, _('Choose directory'), self.ui.edit_directory.text())
        if path:
            self.ui.edit_directory.setText(os.path.normpath(path))

    @staticmethod
    def find(parent, text_to_find=None):
        """
        Shows the dialog for a find operation
        :param parent: parent widget
        :param text_to_find: text to search
        :return: search data or None
        """
        if not text_to_find:
            text_to_find = _last_search_term()
        dlg = _DlgFindReplace(parent, False, text_to_find)
        if dlg.exec_() == dlg.Accepted:
            if dlg.ui.radio_all_projects.isChecked():
                paths = parent.projects
            elif dlg.ui.radio_project.isChecked():
                paths = [dlg.ui.combo_projects.currentText()]
            else:
                paths = [dlg.ui.edit_directory.text()]
            patterns = dlg.ui.edit_pattern.text().strip().split(';')
            search_data = {
                'find': dlg.ui.edit_find.text(),
                'replace': dlg.ui.edit_replace.text(),
                'case_sensitive': dlg.ui.checkbox_case_sensitive.isChecked(),
                'whole_words_only': dlg.ui.checkbox_whole_words.isChecked(),
                'regex': dlg.ui.checkbox_regexp.isChecked(),
                'paths': paths,
                'patterns': [p for p in patterns if p]
            }
            _save_search_data(search_data)
            return search_data
        else:
            return None

    @staticmethod
    def replace(parent, text_to_find=None):
        """
        Shows the dialog for a replace operation.
        :param parent: parent widget
        :param text_to_find: text to search
        :return: search data or None
        """
        if not text_to_find:
            text_to_find = _last_search_term()
        dlg = _DlgFindReplace(parent, True, text_to_find)
        if dlg.exec_() == dlg.Accepted:
            if dlg.ui.radio_all_projects.isChecked():
                paths = parent.projects
            elif dlg.ui.radio_project.isChecked():
                paths = [dlg.ui.combo_projects.currentText()]
            else:
                paths = [dlg.ui.edit_directory.text()]
            patterns = dlg.ui.edit_pattern.text().strip().split(';')
            search_data = {
                'find': dlg.ui.edit_find.text(),
                'replace': dlg.ui.edit_replace.text(),
                'case_sensitive': dlg.ui.checkbox_case_sensitive.isChecked(),
                'whole_words_only': dlg.ui.checkbox_whole_words.isChecked(),
                'regex': dlg.ui.checkbox_regexp.isChecked(),
                'paths': paths,
                'patterns': [p for p in patterns if p]
            }
            _save_search_data(search_data)
            return search_data
        else:
            return None


def _logger():
    return logging.getLogger(__name__)


def search_file(path, search_settings):
    """
    Search occurrences in a file.

    :param path: path of the file to search
    """
    results = []
    string = ''
    for encoding in Cache().preferred_encodings:
        try:
            with open(path, encoding=encoding) as f:
                string = f.read()
        except OSError:
            return
        except UnicodeDecodeError:
            print('failed to open file %r with encoding %s' % (path, encoding))
            continue
        else:
            print('file %r opened with encoding %s' % (path, encoding))
            break
    if string:
        data = {
            'string': None,
            'sub': search_settings['find'],
            'regex': search_settings['regex'],
            'whole_word': search_settings['whole_words_only'],
            'case_sensitive': search_settings['case_sensitive']
        }
        for line_nbr, line in enumerate(string.splitlines()):
            data['string'] = line
            occurrences = findall(data)
            if occurrences:
                results.append((line_nbr, line, occurrences))
    return results


def filter_files(files, search_settings):
    """
    Filter a list of files based on the search settings
    """
    ret_val = []
    patterns = search_settings['patterns']
    for f in files:
        try:
            file_path = f.path
        except AttributeError:
            file_path = f
        for path in search_settings['paths']:
            path += os.sep
            # file is in scope, let's check patterns
            if patterns:
                for pattern in patterns:
                    if fnmatch(file_path, pattern):
                        ret_val.append(file_path)
                        break
                    time.sleep(0)
            else:
                ret_val.append(file_path)
            time.sleep(0)
        time.sleep(0)
    return sorted(list(set(ret_val)))


def get_project_files(project_directories, ignore_patterns):
    ret_val = []
    for directory in project_directories:
        ret_val += get_files_recursively(directory, ignore_patterns)
    return ret_val


def get_files_recursively(directory, ignore_patterns):
    join = os.path.join
    isfile = os.path.isfile
    try:
        dir_paths = listdir(directory)
    except FileNotFoundError:
        return
    for path in dir_paths:
        try:
            path = path.name
        except AttributeError:
            _logger().debug('using the old python api for scanning dirs')
        full_path = join(directory, path)
        ignored = is_ignored_path(full_path, ignore_patterns)
        if not ignored:
            if isfile(full_path):
                yield full_path
            else:
                for path in get_files_recursively(full_path, ignore_patterns):
                    yield path


def get_ignored_patterns(root_project):
    patterns = api.utils.get_ignored_patterns()
    # project specific ignore patterns
    usd = api.project.load_user_config(root_project)
    try:
        patterns += usd['ignored_patterns']
    except KeyError:
        _logger().debug('no ignored patterns found in user config')
    patterns += ['*.exe', '*.dll', '*.usr', '*.so', '*.dylib', '*.psd',
                 '*.db', '.hackedit', '.eggs', '.cache', '.git', '.svn',
                 '.hackedit', 'build', 'dist', '_build']
    return patterns


def search_in_path(th, search_settings):
    """
    Worker function that performs the actual search.
    """
    results = []
    project_directories = search_settings['paths']
    project_files = api.index.get_files(projects=project_directories)
    if not settings.indexing_enabled():
        # indexing disabled or not built yet
        project_files = get_project_files(
            project_directories, get_ignored_patterns(project_directories[0]))
    files = filter_files(project_files, search_settings)
    count = len(files)
    split_path = os.path.split
    for i, f in enumerate(files):
        th.report_progress('searching in %s' % split_path(f)[1],
                           i/count*100)
        occurrences = search_file(f, search_settings)
        if occurrences is not None:
            results.append((f, occurrences))
    return results
