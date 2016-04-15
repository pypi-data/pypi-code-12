from lamiview import __version__, utils
from PyQt5 import Qt
import os.path


class QLamiViewAboutDialog(utils.QCommonDialog, utils.QtUiLoad):
    _UI_NAME = 'dialog_about'

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _set_version(self):
        self._lbl_version.setText('v{}'.format(__version__))

    def _set_contents(self):
        self._set_version()

    def _setup_ui(self):
        self._load_ui()
        self._set_contents()
