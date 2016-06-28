import shutil
import os
import sys

from PyQt5 import QtWidgets

os.environ['PYTEST_QT_API'] = 'pyqt5'
os.environ['QT_API'] = 'pyqt5'
os.environ['HACKEDIT_CORE_TEST_SUITE'] = '1'
os.environ['HACKEDIT_VENDOR_PATH'] = 'hackedit/vendor'
sys.path.insert(0, os.environ['HACKEDIT_VENDOR_PATH'])


from hackedit.main import setup_sqlite3  # noqa
setup_sqlite3()

app = QtWidgets.QApplication(sys.argv)
QtWidgets.qApp.setOrganizationName('HackEdit-TestSuite')
QtWidgets.qApp.setApplicationDisplayName('HackEdit-TestSuite')
QtWidgets.qApp.setApplicationName('HackEdit-TestSuite')


from hackedit.api.gettext import get_translation  # noqa
get_translation()

for pth in ['tests/data/FooBarProj/.hackedit',
            'tests/data/SpamEggsProj/.hackedit',
            'tests/data/SpamEggsProj2/.hackedit',
            'tests/data/SpamEggsProj3/.hackedit']:
    try:
        shutil.rmtree(os.path.join(os.getcwd(), pth))
    except OSError:
        pass

import logging
from hackedit.app import logger

logger.setup(logging.INFO)
