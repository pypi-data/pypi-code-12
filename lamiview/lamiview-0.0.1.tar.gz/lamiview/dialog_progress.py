from lamiview import __version__, utils
from PyQt5 import Qt
import os.path


class QLamiViewProgressDialog(Qt.QDialog, utils.QtUiLoad):
    _UI_NAME = 'dialog_progress'

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self._load_ui()
        self.setModal(True)

        # hide this until we aborting is supported
        self._btn_abort.hide()

    def set_value(self, val):
        self._pb.setValue(int(val * 100))

    def set_message(self, msg):
        self._lbl_msg.setText(msg)

    def reset(self):
        self.set_value(0)
        self.set_message('')

    def closeEvent(self, event):
        event.ignore()

    def show_move(self, pos):
        self.move(pos)
        self.show()
