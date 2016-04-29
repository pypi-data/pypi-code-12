"""
Implementation of pathlib's PurePath and Path for the Qt Resource System,

Use the QRCPATH_QTIMPL environment variable to select PyQt5, PyQt4 or PySide.

@see: http://doc.qt.io/qt-5/resources.html
"""
import os

from qrc_pathlib.version import VERSION


__all__ = ['PureQrcPath', 'QrcPath']
__version__ = VERSION


try:
    QtModuleName = os.getenv('QRCPATH_QTIMPL', '')
    QtModule = __import__(QtModuleName)
except:
    for n in ('PyQt5', 'PyQt4', 'PySide'):
        try:
            QtModuleName = n
            QtModule = __import__(n)
        except ImportError:
            continue
        else:
            break
    else:
        raise ImportError('no Qt implementations found')

QtCore = __import__(QtModuleName + '.QtCore', fromlist=(QtModuleName,))


from qrc_pathlib.pure_qrc_path import PureQrcPath
from qrc_pathlib.qrc_path import QrcPath
