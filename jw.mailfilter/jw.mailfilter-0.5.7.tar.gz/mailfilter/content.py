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
Content checks
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from future import standard_library
from jw.util.python3hell import Bytes2Str

standard_library.install_aliases()
from builtins import *

import re

import logging
from .logging2 import *

class Check(object):
    """
    Check base class
    """

class Has(Check):
    """
    Check for one or more text occurrences

    Checks whether any (at least one) of the arguments appears in the text
    """

    def __init__(self, filterDef, args):
        """
        Create Has object

        """
        self.args = tuple(re.compile(a.strip().lower()) for a in args)
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))

    def check(self, id, content):
        """
        Run check

        :param id: Message ID
        :type id: int
        :param content: content to check
        :type content: str
        :return: True if positive
        :rtype: bool
        """
        lcontent = Bytes2Str(content or '').lower()
        result = any(arg.search(lcontent) for arg in self.args)
        if result:
            self.log.debug('Message %d has some of %s', id, self.args)
        return result

class HasNo(Check):
    def __init__(self, filterDef, args):
        """
        Create HasNo object

        Checks whether none of the arguments appear in the text
        """
        self.args = tuple(re.compile(a.strip().lower()) for a in args)
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))

    def check(self, id, content):
        """
        Run check

        :param id: Message ID
        :type id: int
        :param content: content to check
        :type content: str
        :return: True if positive
        :rtype: bool
        """
        lcontent = Bytes2Str(content or '').lower()
        result = all(not arg.search(lcontent) for arg in self.args)
        if result:
            self.log.debug('Message %d has some of %s', id, self.args)
        return result

class HasAll(Check):
    def __init__(self, filterDef, args):
        """
        Create HasAll object

        Checks whether all arguments appear in the text
        """
        self.args = tuple(re.compile(a.strip().lower()) for a in args)
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))

    def check(self, id, content):
        """
        Run check

        :param id: Message ID
        :type id: int
        :param content: content to check
        :type content: str
        :return: True if positive
        :rtype: bool
        """
        lcontent = Bytes2Str(content or '').lower()
        result = all(arg.search(lcontent) for arg in self.args)
        if result:
            self.log.debug('Message %d has some of %s', id, self.args)
        return result

class Is(Check):
    def __init__(self, filterDef, args):
        """
        Create Has object

        Checks whether text is exactly the arguments
        """
        assert len(args) == 1, 'is check accepts only one argument, got %s' % repr(args)
        self.args = re.compile(Bytes2Str(args[0]).strip().lower(), re.DOTALL | re.MULTILINE)
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))

    def check(self, id, content):
        """
        Run check

        :param id: Message ID
        :type id: int
        :param content: content to check
        :type content: str
        :return: True if positive
        :rtype: bool
        """
        s = Bytes2Str(content or '').strip().lower()
        result = self.args.match(s) is not None
        if result:
            self.log.debug('Message %d match %s', id, self.args.pattern)
        else:
            self.log.log(DEBUG2, 'Message %d %s does not match %s', id, s, self.args.pattern)
        return result

class IsNot(Check):
    def __init__(self, filterDef, args):
        """
        Create Has object

        Checks whether text is not the arguments
        """
        assert len(args) == 1, 'is-not check accepts only one argument, got %s' % repr(args)
        self.args = re.compile(args[0].strip().lower(), re.DOTALL | re.MULTILINE)
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))

    def check(self, id, content):
        """
        Run check

        :param id: Message ID
        :type id: int
        :param content: content to check
        :type content: str
        :return: True if positive
        :rtype: bool
        """
        result = self.args.match(Bytes2Str(content or '').strip().lower()) is None
        if result:
            self.log.debug('Message %d non-match %s', id, self.args.pattern)
        return result

FILTER_FUNCTIONS = {
    'is': Is,
    'is-not': IsNot,
    'has': Has,
    'has-no': HasNo,
    'has-all': HasAll
}
