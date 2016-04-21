# -*- coding: utf-8 -*-

import SiQt
SiQt.use('PyQt4')

from SiQt import QtCore, Qt
print('Qt: {}, PyQt: {}'.format(QtCore.QT_VERSION_STR, Qt.PYQT_VERSION_STR))
