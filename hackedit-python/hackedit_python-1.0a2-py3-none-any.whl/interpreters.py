"""
This module contains a dialog plugin that let the user manage the various
python interpreters and their packages.
"""
import locale
import os
import re
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from hackedit import api
from hackedit.api import plugins, system
from hackedit.api.interpreters import InterpreterManager
from hackedit.api.widgets import PreferencePage, DlgRunProcess

from hackedit_python.forms import settings_page_interpreters_ui, \
    dlg_create_virtualenv_ui
from hackedit_python.system import detect_system_interpreters, \
    is_system_interpreter


_ = api.gettext.get_translation(package='hackedit-python')


class PythonManager(InterpreterManager):
    def __init__(self):
        super().__init__(
            'python', default_interpreter=os.path.realpath(sys.executable),
            mimetype='text/x-python')

    @staticmethod
    def _detect_system_interpreters():
        return detect_system_interpreters()

    @staticmethod
    def get_interpreter_icon():
        if QtGui.QIcon.hasThemeIcon('python'):
            icon = QtGui.QIcon.fromTheme('python')
        else:
            icon = QtGui.QIcon(':/icons/python-logo.png')
        return icon


class ManageInterpreters(plugins.PreferencePagePlugin):
    """
    This plugins lets you manage the python interpreters (add local
    interpreters, create virtualenvs and manage packagesc).
    """
    @staticmethod
    def get_preferences_page():
        return PageManageInterpreters()


class PageManageInterpreters(PreferencePage):
    can_reset = False
    can_restore_defaults = False
    can_apply = False

    def __init__(self):
        super().__init__('Python', PythonManager().get_interpreter_icon())
        self.manager = PythonManager()
        self._ui = settings_page_interpreters_ui.Ui_Form()
        self._ui.setupUi(self)
        self._ui.progress_bar.hide()
        self.setWindowTitle(_('Manage interpreters'))
        self._setup_manage_actions()
        self._load_interpreters()
        self._connect_slots()

    def reset(self):
        pass

    def restore_defaults(self):
        pass

    def save(self):
        pass

    def _setup_manage_actions(self):
        action = QtWidgets.QAction(_('Add local interpreter'),
                                   self._ui.bt_manage_interpreters)
        action.setToolTip(_('Add a local/custom interpreter'))
        action.setIcon(QtGui.QIcon.fromTheme('list-add'))
        action.triggered.connect(self._add_local_interpreter)
        self._ui.bt_manage_interpreters.addAction(action)
        action = QtWidgets.QAction(_('Create virtualenv'),
                                   self._ui.bt_manage_interpreters)
        action.setToolTip(_('Create a new virtual environment'))
        action.setIcon(QtGui.QIcon.fromTheme('list-add'))
        action.triggered.connect(self._create_virtual_env)
        self._ui.bt_manage_interpreters.addAction(action)
        sep = QtWidgets.QAction(self._ui.bt_manage_interpreters)
        sep.setSeparator(True)
        self._ui.bt_manage_interpreters.addAction(sep)
        action = QtWidgets.QAction(_('Remove'),
                                   self._ui.bt_manage_interpreters)
        action.setToolTip(_('Remove current interpreter'))
        action.setIcon(QtGui.QIcon.fromTheme('list-remove'))
        self.action_remove = action
        action.triggered.connect(self._remove_interpreter)
        self._ui.bt_manage_interpreters.addAction(action)

    def _load_interpreters(self):
        self._ui.comboBox.clear()
        self._ui.comboBox.addItems(self.manager.all_interpreters)
        for i in range(self._ui.comboBox.count()):
            if self._ui.comboBox.itemText(i) == \
                    self.manager.default_interpreter:
                self._ui.comboBox.setCurrentIndex(i)
            self._ui.comboBox.setItemIcon(
                i, self.manager.get_interpreter_icon())
        self._on_current_intepreter_changed()

    def _connect_slots(self):
        self._ui.comboBox.currentIndexChanged.connect(
            self._on_current_intepreter_changed)
        self._ui.bt_add_packages.clicked.connect(self._add_packages)
        self._ui.bt_rm_package.clicked.connect(self._rm_package)
        self._ui.bt_update_package.clicked.connect(self._update_package)

    def _add_local_interpreter(self):
        path, filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Add local interpreter'))
        if path:
            self.manager.add_interpreter(os.path.normpath(path))
            self._load_interpreters()

    def _create_virtual_env(self):
        ret = _DlgCreateVirtualEnv.get_virtualenv_creation_params(self)
        if ret is None:
            # dialog canceled
            return
        path, interpreter, global_site_packages = ret
        args = ['-p', interpreter, path]
        if global_site_packages:
            args.insert(0, '--system-site-packages')
        DlgRunProcess.run_process(self, 'virtualenv', args)
        ext = '.exe' if system.WINDOWS else ''
        path = os.path.join(path, 'bin', 'python' + ext)
        self.manager.add_interpreter(path)
        self.manager.default_interpreter = path
        self._load_interpreters()

    def _remove_interpreter(self):
        path = self._ui.comboBox.currentText()
        refresh_required = False
        if path in self.manager.all_interpreters and \
                not is_system_interpreter(path):
            answer = QtWidgets.QMessageBox.question(
                self, _('Remove interpreter'),
                _('Are you sure you want to remove %r?') %
                path)
            if answer == QtWidgets.QMessageBox.Yes:
                self.manager.remove_interpreter(path)
                refresh_required = True
        if refresh_required:
            self.manager.default_interpreter = sys.executable
            self._load_interpreters()

    def _add_packages(self):
        packages, status = QtWidgets.QInputDialog.getText(
            self, _('Install packages'), _('Packages: '))
        if not status:
            return
        interpreter = self._ui.comboBox.currentText()
        packages = packages.split(' ')
        if not os.access(self._ui.comboBox.currentText(), os.W_OK):
            pgm = system.get_authentication_program()
            if not pgm:
                QtWidgets.QMessageBox.warning(
                    self, _('No authentification program found'),
                    _('No authentification program found...\n\n'
                      'Please install one of these tools: gksu or kdesu'))
                return
            args = ['--', interpreter, '-m', 'pip', 'install'] + packages
            if pgm == 'kdesu':
                args.insert(0, '-t')
            if pgm == 'beesu':
                args = args[1:]
        else:
            pgm = interpreter
            args = ['-m', 'pip', 'install'] + packages
        DlgRunProcess.run_process(self, pgm, arguments=args)
        self._clear_table()
        self.check_packages(interpreter)

    def _rm_package(self):
        packages = []
        for item in self._ui.tableWidget.selectedItems():
            if item.column() == 0:
                packages.append(item.text())
        if not packages:
            return
        answer = QtWidgets.QMessageBox.question(
            self, _('Remove packages', 'Are you sure you want to remove the '
                    'following packages: \n\n  -') + '\n  - '.join(packages))
        if answer == QtWidgets.QMessageBox.No:
            return
        interpreter = self._ui.comboBox.currentText()
        if not os.access(self._ui.comboBox.currentText(), os.W_OK):
            pgm = system.get_authentication_program()
            if not pgm:
                QtWidgets.QMessageBox.warning(
                    self, _('No authentification program found'),
                    _('No authentification program found...\n\n'
                      'Please install one of those tools: gksu or kdesu'))
                return
            args = ['--', interpreter, '-m', 'pip', 'uninstall'] + \
                packages + ['-y']
            if pgm == 'kdesu':
                args.insert(0, '-t')
        else:
            pgm = interpreter
            args = ['-m', 'pip', 'uninstall'] + packages + ['-y']
        DlgRunProcess.run_process(self, pgm, arguments=args)
        self._clear_table()
        self.check_packages(interpreter)

    def _update_package(self):
        packages = []
        for item in self._ui.tableWidget.selectedItems():
            if item.column() == 0:
                packages.append(item.text())
        if not packages:
            return
        answer = QtWidgets.QMessageBox.question(
            self, _('Update packages'),
            _('Are you sure you want to update the following packages: '
              '\n\n  -') + '\n  - '.join(packages))
        if answer == QtWidgets.QMessageBox.No:
            return
        interpreter = self._ui.comboBox.currentText()
        if not os.access(self._ui.comboBox.currentText(), os.W_OK):
            pgm = system.get_authentication_program()
            if not pgm:
                QtWidgets.QMessageBox.warning(
                    self, _('No authentification program found'),
                    _('No authentification program found...\n\n'
                      'Please install one of those tools: gksu or kdesu'))
                return
            args = ['--', interpreter, '-m', 'pip', 'install'] + \
                packages + ['--upgrade']
            if pgm == 'kdesu':
                args.insert(0, '-t')
        else:
            pgm = interpreter
            args = ['-m', 'pip', 'install'] + packages + ['--upgrade']
        DlgRunProcess.run_process(self, pgm, arguments=args)
        self._clear_table()
        self.check_packages(interpreter)

    def _clear_table(self):
        self._ui.tableWidget.clear()
        self._ui.tableWidget.clearSelection()
        self._ui.tableWidget.setColumnCount(2)
        header = self._ui.tableWidget.horizontalHeader()
        header.setStretchLastSection(True)
        self._ui.tableWidget.setHorizontalHeaderLabels(['Package', 'Version'])

    def _on_current_intepreter_changed(self):
        self._clear_table()
        self.check_packages(self._ui.comboBox.currentText())
        path = self._ui.comboBox.currentText()
        self.action_remove.setEnabled(path in self.manager.all_interpreters and
                                      not is_system_interpreter(path))
        self.manager.default_interpreter = self._ui.comboBox.currentText()

    def check_packages(self, path):
        self._process = QtCore.QProcess()
        self._process.setProcessChannelMode(self._process.MergedChannels)
        self._process.finished.connect(self._on_package_list_available)
        self._process.start(path, ['-m', 'pip', 'list'])
        self._ui.progress_bar.show()

    def _on_package_list_available(self):
        self._ui.progress_bar.hide()
        if self._process.exitCode() != 0:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText(_('Failed to retrieve package list'))
            msg_box.setInformativeText(
                _('We could not retrieve the list of packages for %s.\n')
                % self._ui.comboBox.currentText())
            msg_box.setIcon(msg_box.Warning)
            msg_box.setDetailedText(
                bytes(self._process.readAllStandardOutput()).decode(
                    locale.getpreferredencoding()))
            msg_box.exec_()
            return
        lines = bytes(self._process.readAllStandardOutput()).decode(
            locale.getpreferredencoding()).splitlines()
        items = []
        for i, l in enumerate(lines):
            if re.match(r'.* \(.*\)', l):
                package = re.match(r'.* \(', l).group(0).replace(' (', '')
                version = l.split(' ')[1].replace('(', '').replace(')', '')
            elif re.match(r'.* \(.*, .*\)', l):
                package = re.match('.* \(', l).group(0).replace(' (', '')
                version = l.split(' ')[1].split(',')[0].replace('(', '')
            else:
                continue
            version = version.replace(',', '')
            if 'hackedit' in package and \
                    self._ui.comboBox.currentText() != sys.executable:
                continue
            items.append((package, version))
        self._ui.tableWidget.setRowCount(len(items))
        for i, item in enumerate(items):
            package, version = item
            self._ui.tableWidget.setItem(
                i, 0, QtWidgets.QTableWidgetItem(package))
            self._ui.tableWidget.setItem(
                i, 1, QtWidgets.QTableWidgetItem(version))
        self._ui.tableWidget.resizeColumnToContents(0)


class _DlgCreateVirtualEnv(QtWidgets.QDialog):
    def __init__(self, parent):
        super(_DlgCreateVirtualEnv, self).__init__(parent)
        self._ui = dlg_create_virtualenv_ui.Ui_Dialog()
        self._ui.setupUi(self)
        self._load_interpreters()
        self._ui.edit_name.textChanged.connect(self._update_full_path)
        self._ui.edit_name.setText(_('unnamed'))
        self._ui.edit_dir.setText(os.path.join(os.path.expanduser('~')))
        self._ui.edit_dir.textChanged.connect(self._update_full_path)
        self._ui.bt_dir.clicked.connect(self._pick_dir)
        self._update_full_path()

    def _load_interpreters(self):
        manager = PythonManager()
        self._ui.combo_interpreters.clear()
        self._ui.combo_interpreters.addItems(manager.all_interpreters)
        for i in range(self._ui.combo_interpreters.count()):
            if self._ui.combo_interpreters.itemText(i) == \
                    manager.default_interpreter:
                self._ui.combo_interpreters.setCurrentIndex(i)

    def _pick_dir(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, _('Choose directory'), self._ui.edit_dir.text())
        self._ui.edit_dir.setText(os.path.normpath(path))

    @staticmethod
    def _set_widget_background_color(widget, color):
        """
        Changes the base color of a widget (background).
        :param widget: widget to modify
        :param color: the color to apply
        """
        pal = widget.palette()
        pal.setColor(pal.Base, color)
        widget.setPalette(pal)

    def _update_full_path(self):
        path = os.path.join(self._ui.edit_dir.text(),
                            self._ui.edit_name.text())
        exists = os.path.exists(path)
        self._ui.buttonBox.button(self._ui.buttonBox.Ok).setEnabled(not exists)
        self._ui.label_full_path.setText(path)
        color = QtGui.QColor('#FFCCCC') if exists else self.palette().color(
            self.palette().Base)
        self._set_widget_background_color(self._ui.edit_name, color)
        self._ui.edit_name.setToolTip(
            _('Path already exists') if exists else '')

    @property
    def path(self):
        """
        Gets the full path of the virtualenv to create.
        """
        return self._ui.label_full_path.text()

    @property
    def interprerer(self):
        """
        Gets the base interpreter to use for creating the new virtualenv.
        """
        return self._ui.combo_interpreters.currentText()

    @property
    def use_system_site_packages(self):
        """
        Gets the flags that specifies if the new virtualenv can use the system
        site packages for searching for python packages.
        """
        return self._ui.check_box_site_packages.isChecked()

    @classmethod
    def get_virtualenv_creation_params(cls, parent):
        """
        Show the dialog and return the information needed to create the
        virtualenv. Returns None if the dialog has been canceled.
        """
        dlg = cls(parent)
        if dlg.exec_() == dlg.Accepted:
            return dlg.path, dlg.interprerer, dlg.use_system_site_packages
        else:
            return None
