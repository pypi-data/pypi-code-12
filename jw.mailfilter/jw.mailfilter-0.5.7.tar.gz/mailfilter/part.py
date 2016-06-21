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
Part extraction functions
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from future import standard_library

standard_library.install_aliases()
from builtins import *
from builtins import str
from builtins import object

class Part(object):
    """
    Part base class
    """

class Body(Part):
    """
    Extract body from message

    All body parts are extracted, decoded and returned as one string
    """

    def __init__(self, filterDef):
        """
        Create Body object

        :param filterDef: filter definition
        :type filterDef: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))

    def __call__(self, message):
        """
        Get message part

        :return: message part
        :rtype: str
        """
        return self.extract(message)

    @staticmethod
    def extract(message):
        """
        Extract payload

        :param message:
        :type message:
        :return:
        :rtype:
        """
        if message.is_multipart():
            return ''.join(Body.extract(m) for m in message.get_payload())
        else:
            return message.get_payload(decode=True) or message.get_payload()

PART_FUNCTIONS = {
    'body': Body
}
