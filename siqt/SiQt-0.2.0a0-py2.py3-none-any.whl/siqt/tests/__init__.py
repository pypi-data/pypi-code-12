#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
from .run_suite import run, run_cli

def get_system_info(pretty_print=False):
    import siqt
    from siqt import QtCore
    import platform
    system = {}
    for key in ['architecture', 'machine', 'platform', 'processor',
                'system']:
        system[key] = getattr(platform, key)()

    # platform specific stuff
    for key in ['win32_ver', 'mac_ver', 'linux_distribution']:
        res = getattr(platform, key)()
        if res[0]:
            system[key] = res
    if  sys.maxsize > 2**32:
        system['architecture_size'] = '64 bits'
    else:
        system['architecture_size'] = '32 bits'

    python = {}
    for key in [ 'python_implementation', 'python_version', 'python_compiler']:
        python[key] = getattr(platform, key)()

    sv = {}
    try:
        import numpy as np
        sv['numpy'] = np.__version__
    except ImportError:
        sv['numpy'] = 'Not installed'

    try:
        import scipy
        sv['scipy'] = scipy.__version__
    except ImportError:
        sv['scipy'] = "Not installed"

    try:
        import pandas as pd
        sv['pandas'] = pd.__version__
    except ImportError:
        sv['pandas'] = "Not installed"
    try:
        import matplotlib as mpl
        sv['matplotlib'] = mpl.__version__
    except ImportError:
        sv['matplotlib'] = "Not installed"
    if 'PyQt' in siqt.SIQT_BACKEND:
        from siqt import Qt
        sv['Qt'] = QtCore.QT_VERSION_STR
        sv['PyQt'] = Qt.PYQT_VERSION_STR
    elif 'PySide' in siqt.SIQT_BACKEND:
        import PySide
        sv['Qt'] = QtCore.__version__
        sv['PySide'] = PySide.__version__
    else:
        raise NotImplementedError



    if not pretty_print:
        return {'system': system, 'python': python, 'software_versions': sv}
    else:
        FMT = '   {:12}: {}'
        s = []
        for label, mdict in [('System information', system),
                             ('Python version', python),
                             ('Included modules', sv)]:
            s += ['', label, '='*30, '']
            for key, val in mdict.items():
                if type(val) is tuple:
                    val = ' '.join(val)
                s.append(FMT.format(key, val))
        s.append('')
        

        return '\n'.join(s)
