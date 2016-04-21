# -*- coding: utf-8 -*-

import imp
import sys

name = "QtCore"
path = ['/usr/lib64/python2.7/site-packages/PyQt4']


def load_module(name, path):
    import sip
    import importlib
    print(name, path)
    fp, pathname, description = imp.find_module(name, path)
    print(sys.modules.keys())

    try:
        module = imp.load_module(name, fp, pathname, description)
    except:
        module = importlib.import_module('PyQt4.QtCore') #__import__('PyQt4.QtCore', globals(), locals(), [], -1)
    finally:
        if fp:
            fp.close()
    return module

mod = load_module(name, path)
print(mod.QT_VERSION_STR)



