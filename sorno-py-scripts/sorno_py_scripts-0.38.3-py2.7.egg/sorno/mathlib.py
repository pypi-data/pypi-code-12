"""A library for math related things


Copyright 2015 Heung Ming Tai

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple


class Interval(object):
    """An interval with a starting and a ending points, open or closed.

    It's a read-only class.

    Attributes:
        start (int or float): The starting point of the interval.
        end (int or float): The ending point of the interval.
        is_start_opened (Optional[bool]): True if the starting point is open.
            It's False by default.
        is_end_opened (Optional[bool]): True if the ending point is open.
            It's False by default.
    """
    def __init__(self, start, end, is_start_opened=False, is_end_opened=False):
        self._start = start
        self._end = end
        self._is_start_opened = is_start_opened
        self._is_end_opened = is_end_opened

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def is_start_opened(self):
        return self._is_start_opened

    @property
    def is_end_opened(self):
        return self._is_end_opened

    def __str__(self):
        tmp = "Interval(start=%r,end=%r,is_start_opened=%r,is_end_opened=%r)"
        return tmp % (
            self._start,
            self._end,
            self._is_start_opened,
            self._is_end_opened,
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False

        return (
            self._start,
            self._end,
            self._is_start_opened,
            self._is_end_opened,
        ) == (
            other._start,
            other._end,
            other._is_start_opened,
            other._is_end_opened,
        )
