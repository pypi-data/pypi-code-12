import os
from PyQt5 import QtWidgets
from hackedit.app.forms import dlg_ignore_file_ui


class DlgIgnore(QtWidgets.QDialog):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.ui = dlg_ignore_file_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.edit_pattern.setText('*%s' % os.path.splitext(name)[1])

    @staticmethod
    def get_ignore_pattern(parent, name):
        dlg = DlgIgnore(parent, name)
        if dlg.exec_() == dlg.Accepted:
            if dlg.ui.rb_explicit.isChecked():
                return name
            else:
                return dlg.ui.edit_pattern.text()
        return None
