# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .. import this

import matplotlib

if this.backend == 'PyQt4':
    PyQtAgg_str = 'Qt4Agg'
    matplotlib.use(PyQtAgg_str)
    matplotlib.rcParams['backend.qt4'] = this.backend
    import matplotlib.backends.backend_qt4agg as backend_qtagg
elif this.backend == 'PySide':
    PyQtAgg_str = this.backend
    matplotlib.use('Qt4Agg')
    matplotlib.rcParams['backend.qt4'] = this.backend
    import matplotlib.backends.backend_qt4agg as backend_qtagg
elif this.backend == 'PyQt5':
    PyQtAgg_str = 'Qt5Agg'
    matplotlib.use(PyQtAgg_str)
    matplotlib.rcParams['backend.qt5'] = this.backend
    import matplotlib.backends.backend_qt5agg as backend_qtagg
else:
    raise NotImplementedError

def _matplotlib_use(*pargs, **cargs):
    print('Warning: matplotlib.use was called by SiQt for the {} backend.\n'.format(this.backend) +\
     '       Calling it a second time will have no effect!')

matplotlib.use = _matplotlib_use

class NavigationToolbar(backend_qtagg.NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in backend_qtagg.NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]
