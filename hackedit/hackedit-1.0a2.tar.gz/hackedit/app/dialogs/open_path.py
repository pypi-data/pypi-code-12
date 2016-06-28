import os

from PyQt5 import QtWidgets

from hackedit.app import settings
from hackedit.app.forms.dlg_open_ui import Ui_Dialog


class DlgOpen(QtWidgets.QDialog):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        name = _('file') if os.path.isfile(path) else _('project')
        self.setWindowTitle(_('Open %s') % name)
        self.ui.label.setText(self.ui.label.text() % name)

    @classmethod
    def get_open_mode(cls, parent, path):
        """
        Returns the open mode.

        :param parent: parent widget
        :return: 0 for open in new window, 1 for open in current and None if
                 the dialog was rejected.
        """
        if settings.open_mode() == settings.OpenMode.ASK_EACH_TIME:
            dlg = cls(parent, path)
            if dlg.exec_() == dlg.Accepted:
                return 0 if dlg.ui.rb_open_new.isChecked() else 1
        else:
            return settings.open_mode()
        return None
