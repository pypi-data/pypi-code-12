# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
from unittest.case import SkipTest
from multiprocessing import Process, Queue
from time import sleep, time


def _run_process(func):
    @functools.wraps(func)
    def inner_wrapper(*args):
        def func_wrapper(func, q, args):
            try:
                res = func(*args)
                q.put(res)
            except Exception as e:
                q.put(e)

        q = Queue()
        p = Process(target=func_wrapper, args=(func, q, args))
        p.start()

        result = q.get(block=True)
        if isinstance(result, Exception):
            raise result

        return result
    return inner_wrapper


@_run_process
def _check_importer(backend):
    import SiQt
    try:
        import SiQt.QtCore
    except ImportError:
        assert True  # this is normal
    except:
        raise
    try:
        SiQt.use(backend, force=False)
    except ImportError:
        raise SkipTest
    except:
        raise
    import SiQt.QtCore


def test_PyQt4_importer():
    _check_importer('PyQt4')

def test_PyQt5_importer():
    _check_importer('PyQt5')

def test_PySide_importer():
    _check_importer('PySide')
