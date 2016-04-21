# -*- coding: utf-8 -*-

import SiQt
SiQt.use('PyQt5', force=True)

import PyQt4
from PyQt4 import QtCore

print('PyQt4.__name__              :', PyQt4.__name__)
print('SiQt.backend                :', SiQt.backend)
print('PyQt4.QtCore.QT_VERSION_STR :', QtCore.QT_VERSION_STR)
