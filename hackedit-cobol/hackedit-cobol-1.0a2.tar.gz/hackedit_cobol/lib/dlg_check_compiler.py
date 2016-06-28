from PyQt5 import QtCore, QtWidgets

from hackedit import api
from hackedit.api import system
from hackedit_cobol.lib.compiler import GnuCOBOLCompiler
from hackedit_cobol.forms import dlg_check_compiler_ui


_ = api.gettext.get_translation(package='hackedit-cobol')


class DlgCheckCompiler(QtWidgets.QDialog):
    def __init__(self, config, parent):
        super().__init__(
            parent, QtCore.Qt.WindowSystemMenuHint |
            QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.config = config
        self.ui = dlg_check_compiler_ui.Ui_Dialog()
        self.ui.setupUi(self)
        version = GnuCOBOLCompiler.get_version(config, include_all=True)
        self.ui.textEdit.setText(version)
        self.ui.buttonBox.button(self.ui.buttonBox.Apply).setText(
            _('Check compilation'))
        self.ui.buttonBox.button(self.ui.buttonBox.Apply).clicked.connect(
            self._check_compiler)
        self.ui.buttonBox.button(self.ui.buttonBox.Apply).setDisabled(
            not version)

    def _check_compiler(self):
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.WaitCursor)
        exit_code, output = GnuCOBOLCompiler.check_compiler(self.config)
        dark = QtWidgets.qApp.palette().base().color().lightness() < 128
        if exit_code == 0:
            if dark:
                self.ui.textEdit.setTextColor(QtCore.Qt.green)
            else:
                self.ui.textEdit.setTextColor(QtCore.Qt.darkGreen)
            msg = _('Compiler works!')
            self.ui.textEdit.setText(msg)
        else:
            msg = _('<h1>GnuCOBOLCompiler check failed!</h1>')
            self.ui.textEdit.setText(msg)
            self.ui.textEdit.append(
                _('<p><b>Exit code<b>: %d</p>' % exit_code))
            self.ui.textEdit.append(
                _('<p><h2>GnuCOBOLCompiler output:</h2></p>'))
            self.ui.textEdit.setTextColor(QtCore.Qt.red)
            self.ui.textEdit.append(output.strip())
            tips = _('<h2>Tips:</h2><p><i>  - You might need to adapt the '
                     'environment variables set by the IDE to make it work.'
                     '</i></p>')
            if system.WINDOWS:
                tips += _(
                    "<p><i>  - Also make sure that you don't have a "
                    'conflicting installation of MinGW at the root of '
                    'the drive where you installed HackEdit.</i></p>')
            self.ui.textEdit.append(tips)
        QtWidgets.qApp.restoreOverrideCursor()

    @classmethod
    def check(cls, parent, config):
        dlg = cls(config, parent)
        return dlg.exec_() == dlg.Accepted
