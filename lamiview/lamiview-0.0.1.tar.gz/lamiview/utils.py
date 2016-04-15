# The MIT License (MIT)
#
# Copyright (c) 2016 Philippe Proulx <pproulx@efficios.com>
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

from pkg_resources import resource_filename
from PyQt5 import Qt, QtGui, uic
import os.path


class QCommonDialog(Qt.QDialog):
    def __init__(self):
        super().__init__()

    def show_move(self, pos):
        self.move(pos)
        self.exec()


class QtUiLoad:
    def _load_ui(self):
        ui_rel_path = os.path.join('res', 'ui', '{}.ui'.format(self._UI_NAME))
        ui_path = resource_filename(__name__, ui_rel_path)
        uic.loadUi(ui_path, baseinstance=self)


def get_res_path(name):
    rel_path = os.path.join('res', name)
    path = resource_filename(__name__, rel_path)

    return path


def get_qicon(name):
    filename = '{}.png'.format(name)
    path = get_res_path(os.path.join('icons', filename))

    return Qt.QIcon(path)


def set_widget_icon(widget, name, size=16):
    icon = get_qicon(name)
    widget.setIcon(icon)
    widget.setIconSize(Qt.QSize(size, size))


def set_widget_icons(entries, size=16):
    for entry in entries:
        set_widget_icon(entry[0], entry[1], size)


def goto_url(url):
    QtGui.QDesktopServices.openUrl(Qt.QUrl(url))


def usec_to_sec(usec):
    return int(usec) / 1000000


def sec_to_usec(sec):
    return round(sec * 1000000)


def bytes_to_human_prefix(b):
    if b < (1 << 10):
        return (b, 'b')
    elif b < (1 << 20):
        return (b / (1 << 10), 'k')
    elif b < (1 << 30):
        return (b / (1 << 20), 'm')
    else:
        return (b / (1 << 30), 'g')


def bytes_to_human(b):
    prefix_map = {
        'b': 'B',
        'k': 'kiB',
        'm': 'MiB',
        'g': 'GiB',
    }
    b, prefix = bytes_to_human_prefix(b)

    return '{} {}'.format(b, prefix_map[prefix])


# Copyright (C) 2016 - Antoine Busque <abusque@efficios.com>
# MIT license
def format_timestamp(timestamp, print_date=False, gmt=False):
    import time

    NSEC_PER_SEC = 1000000000

    """Format a timestamp into a human-readable date string

    Args:
        timestamp (int): nanoseconds since epoch.

        print_date (bool, optional): flag indicating whether to print
        the full date or just the time of day (default: False).

        gmt (bool, optional): flag indicating whether the timestamp is
        in the local timezone or gmt (default: False).

    Returns:
        The formatted date string, containing either the full date or
        just the time of day.
    """
    date_fmt = '{:04}-{:02}-{:02} '
    time_fmt = '{:02}:{:02}:{:02}.{:09}'

    if gmt:
        date = time.gmtime(timestamp / NSEC_PER_SEC)
    else:
        date = time.localtime(timestamp / NSEC_PER_SEC)

    formatted_ts = time_fmt.format(
        date.tm_hour, date.tm_min, date.tm_sec,
        timestamp % NSEC_PER_SEC
    )

    if print_date:
        date_str = date_fmt.format(date.tm_year, date.tm_mon, date.tm_mday)
        formatted_ts = date_str + formatted_ts

    return formatted_ts


# Copyright (C) 2016 - Antoine Busque <abusque@efficios.com>
# MIT license
def format_size(size, binary_prefix=True):
    import math

    """Convert an integral number of bytes to a human-readable string.

    Args:
        size (int): a non-negative number of bytes.

        binary_prefix (bool, optional): whether to use binary units
        prefixes, over SI prefixes (default: True).

    Returns:
        The formatted string comprised of the size and units.

    Raises:
        ValueError: if size < 0.
    """
    if size < 0:
        raise ValueError('Cannot format negative size')

    if binary_prefix:
        base = 1024
        units = ['  B', 'kiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    else:
        base = 1000
        units = [' B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    if size == 0:
        exponent = 0
    else:
        exponent = int(math.log(size, base))
        if exponent >= len(units):
            # Don't try and use a unit above YiB/YB
            exponent = len(units) - 1

        size /= math.pow(base, exponent)

    unit = units[exponent]

    if exponent == 0:
        # Don't display fractions of a byte
        format_str = '{:0.0f} {}'
    else:
        format_str = '{:0.2f} {}'

    return format_str.format(size, unit)
