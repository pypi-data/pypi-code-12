# This file is part of the Online Services test tools
#
# Copyright 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import re


class NameMatcher(object):
    """Defines rules to select names.

    The rules are defined by two lists of regular expressions:
    - includes: matching succeeds if one of the regular expression match.
    - excludes: matching fails if one of the regular expression match.

    Matching fails if no rules are given.
    """

    def __init__(self, includes=None, excludes=None):
        self.includes = []
        if includes is not None:
            for inc in includes:
                self.includes.append(re.compile(inc))
        self.excludes = []
        if excludes is not None:
            for exc in excludes:
                self.excludes.append(re.compile(exc))

    def matches(self, name):
        for exc in self.excludes:
            if exc.search(name):
                return False
        for inc in self.includes:
            if inc.search(name):
                return True
        # Not explicitely included
        return False
