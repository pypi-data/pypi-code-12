# Author: Tom Richter

# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
                bytes, dict, int, list, object, range, str,
                ascii, chr, hex, input, next, oct, open,
                pow, round, super,
                filter, map, zip)

import contextlib
import os
import shutil
import sys
import tempfile

@contextlib.contextmanager
def quiet():
    stdout_save = sys.stdout
    class Devnull(object):
        def write(self, _):
            pass
    sys.stdout = Devnull()
    try:
        yield
    finally:
        sys.stdout = stdout_save

@contextlib.contextmanager
def tempdir(delete=True, change_dir=True):
    if delete:
        tempdir = tempfile.mkdtemp(prefix='codamag_test')
    else:
        tempdir = os.path.join(tempfile.gettempdir(), 'codamag_test_permanent')
        if not os.path.exists(tempdir):
            os.mkdir(tempdir)
    if change_dir:
        os.chdir(tempdir)
    try:
        yield tempdir
    finally:
        if delete and os.path.exists(tempdir):
            shutil.rmtree(tempdir)