# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Utilities
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals, print_function

from future import standard_library

from .header import decode_header

standard_library.install_aliases()
from builtins import *
import re

FromRe = re.compile(
    r'from\s+(?:'
    r'.*\(.*\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]\)'
    '|'
    r'.*?\(.*?\)\s*?\((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)'
    r').*'
)

def D(prompt, value):
    print('{}: {}'.format(prompt, value))
    return value

def Flatten(items):
    """
    Flatten a list

    :param items:
    :type items: list
    :return: flattened list
    :rtype: iter
    """
    if isinstance(items, (list, tuple)):
        for item in items:
            if isinstance(item, (list, tuple)):
                for subitem in Flatten(item):
                    yield subitem
            else:
                yield item
    else:
        yield items

def DecodeHeader(header):
    try:
        d = decode_header(header)
        return ''.join(p[0].decode(p[1] or 'ascii', 'replace') for p in d)
    except Exception as e:
        return header
