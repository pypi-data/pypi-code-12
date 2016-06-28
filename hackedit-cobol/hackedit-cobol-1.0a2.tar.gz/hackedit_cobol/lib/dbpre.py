"""
Contains the code specific to dbpre preparser integration.
"""
import os
from PyQt5 import QtWidgets
from hackedit import api

from hackedit_cobol.forms import dlg_dbpre_ui


_ = api.gettext.get_translation(package='hackedit-cobol')

DBPRE_NAME = 'SQL COBOL (dbpre)'
STYLE_ERROR = 'background-color: #DD8080;color: white;'
STYLE_OK = ''


DBPRE_CONFIG = {
    'name': 'SQL COBOL (dbpre)',
    'associated-extensions': ['*.scb'],
    'path': '',  # to be filled
    'flags': '$file -I%s -ts=4',  # %s = path to framework
    'only-preparser': False,
    'output-rule': '$file.cob',
    'extra-cobol-compiler-flags':
        # /path/to/cobmysqlapi.o
        '%s '
        # /path/to/framework
        '-I%s '
        '-L/usr/lib/mysql -lmysqlclient'
}


class DlgDbpreConfig(QtWidgets.QDialog):
    """
    A dialog for first time config of dbpre.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = dlg_dbpre_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.edit_exe.textChanged.connect(self._validate)
        self.ui.edit_obj.textChanged.connect(self._validate)
        self.ui.edit_copy.textChanged.connect(self._validate)
        self.ui.bt_copy.clicked.connect(self._select_copy)
        self.ui.bt_exe.clicked.connect(self._select_exe)
        self.ui.bt_obj.clicked.connect(self._select_obj)
        self._validate()

    def _validate(self, *_):
        ok = True

        # check exe
        exe = self.ui.edit_exe.text()
        if not exe or not os.path.exists(exe) or not os.path.isfile(exe):
            ok = False
            self.ui.edit_exe.setStyleSheet(STYLE_ERROR)
        else:
            self.ui.edit_exe.setStyleSheet(STYLE_OK)

        # check obj file
        obj = self.ui.edit_obj.text()
        if not obj or not os.path.exists(obj) or not os.path.isfile(obj):
            ok = False
            self.ui.edit_obj.setStyleSheet(STYLE_ERROR)
        else:
            self.ui.edit_obj.setStyleSheet(STYLE_OK)

        # check copybook path
        cpy = self.ui.edit_copy.text()
        if not cpy or not os.path.exists(cpy) or not os.path.isdir(cpy):
            ok = False
            self.ui.edit_copy.setStyleSheet(STYLE_ERROR)
        else:
            self.ui.edit_copy.setStyleSheet(STYLE_OK)

        self.ui.buttonBox.button(self.ui.buttonBox.Ok).setEnabled(ok)

    def get_open_file_dialog_directory(self):
        obj = self.ui.edit_obj.text()
        if obj:
            return os.path.dirname(obj)

        exe = self.ui.edit_exe.text()
        if exe:
            return os.path.dirname(exe)

        return self.ui.edit_copy.text()

    def _select_exe(self):
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Select dbpre executable'),
            directory=self.get_open_file_dialog_directory())
        if path:
            self.ui.edit_exe.setText(os.path.normpath(path))

    def _select_obj(self):
        path, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self, _('Select cobmysqlapi.o'),
            filter=_('Object file (*.o *.obj)'),
            directory=self.get_open_file_dialog_directory())
        if path:
            self.ui.edit_obj.setText(os.path.normpath(path))

    def _select_copy(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, _('Select dbpre copybooks directory'),
            directory=self.get_open_file_dialog_directory())
        if path:
            self.ui.edit_copy.setText(os.path.normpath(path))

    @staticmethod
    def get_configuration(parent):
        dlg = DlgDbpreConfig(parent)
        if dlg.exec_():
            name, exe, obj, cpy = (DBPRE_NAME,
                                   dlg.ui.edit_exe.text(),
                                   dlg.ui.edit_obj.text(),
                                   dlg.ui.edit_copy.text())
            cfg = DBPRE_CONFIG.copy()
            extra = cfg['extra-cobol-compiler-flags']
            cfg['extra-cobol-compiler-flags'] = extra % (obj, cpy)
            cfg['flags'] = cfg['flags'] % cpy
            cfg['name'] = name
            cfg['path'] = exe
            return cfg

        return None
