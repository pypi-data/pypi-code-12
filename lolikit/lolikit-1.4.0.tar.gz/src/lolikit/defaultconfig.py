#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import os
import sys
from collections import OrderedDict as OD


def _get_default_editor():
    if sys.platform.startswith('linux'):
        return 'xdg-open'
    elif sys.platform.startswith('darwin'):
        return 'open'
    elif sys.platform.startswith('win'):
        return 'cmd /c \'{path}\''


def _get_default_file_browser():
    if sys.platform.startswith('linux'):
        return 'xdg-open'
    elif sys.platform.startswith('darwin'):
        return 'open'
    elif sys.platform.startswith('win'):
        return 'cmd /c \'{path}\''


def _get_default_newline_mode():
    if os.linesep == '\n':
        return 'posix'
    elif os.linesep == '\r':
        return 'mac'
    elif os.linesep == '\r\n':
        return 'windows'
    else:
        return 'posix'


DEFAULT_CONFIG = OD((
    ('user', OD((
        ('default_project', ""),
        ))),
    ('project', OD((
        ('ignore_patterns', ''),
        # ^ multiple patterns split by newline
        # all pathname string start with the rootdir
        # auto include: '^.loli($|' + os.sep + ')'
        ))),
    ('selector', OD((
        ('editor', _get_default_editor()),
        ('file_browser', _get_default_file_browser()),
        ('reverse', 'no'),
        ('page_size', 10),
        ('find_format', '{prepend_resourced_icon}{title}  <<  {category}'),
        ('list_format',
            '[{mtime:%%m/%%d %%H:%%M}] {prepend_resourced_icon}{title}'),
        ))),
    ('check', OD((
        ('danger_pathname_chars', '\\/:"*?<>|'),
        ('danger_pathname_chars_fix_to', '='),
        ('newline_mode', _get_default_newline_mode()),
        # ^ one of 'windows', 'mac', 'posix'
        # default == current system mode
        ))),
    ('serve', OD((
        ('port', '10204'),
        ('allow_remote_access', 'no'),
        ('debug', 'no'),
        ('users', ''),
        ('ssl_cert_file', ''),
        ))),
    ))
