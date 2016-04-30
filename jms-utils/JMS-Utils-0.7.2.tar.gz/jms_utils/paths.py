# --------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014-2016 Digital Sapphire
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# --------------------------------------------------------------------------
import logging
import os
import shutil
import sys
import time
import warnings

from jms_utils.app import _app_cwd

log = logging.getLogger(__name__)


# ToDo: Remove in v1.0
def warn():
    warnings.warn('Will be remove in v1.0: app_cwd moved to jms_utils.app.app_cwd',
                  DeprecationWarning)
    return _app_cwd()

app_cwd = warn()
# End ToDo


def remove_any(path):

    def _remove_any(x):
        if os.path.isdir(x):
            shutil.rmtree(x, ignore_errors=True)
        else:
            os.remove(path)

    if sys.platform != 'win32':
        _remove_any(path)
    else:
        for _ in range(100):
            try:
                _remove_any(path)
            except Exception as err:
                log.debug(err, exc_info=True)
                time.sleep(0.01)
            else:
                break
        else:
            try:
                _remove_any(path)
            except Exception as err:
                log.debug(err, exc_info=True)


class ChDir(object):
    """Used as a context manager to step into a directory
    do some work then return to the original directory.

    Args:

        path (str): Absolute path to directory you want to change to
    """
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        log.debug(u'Changing to Directory --> {}'.format(self.new_dir))
        os.chdir(self.new_dir)

    def __exit__(self, *args, **kwargs):
        log.debug(u'Moving back to Directory --> {}'.format(self.old_dir))
        os.chdir(self.old_dir)
