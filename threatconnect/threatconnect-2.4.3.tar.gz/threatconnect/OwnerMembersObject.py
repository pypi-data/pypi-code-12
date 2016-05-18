""" standard """
import csv
import json
import urllib
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

""" custom """

import ApiProperties
from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes
from RequestObject import RequestObject


def parse_member(member):
    """ """
    # member object
    om = OwnerMembersObject()

    om.set_user_name(member['userName'])
    om.set_first_name(member['firstName'])
    om.set_last_name(member['lastName'])

    return om


class OwnerMembersObject(object):
    __slots__ = (
        '_user_name',
        '_first_name',
        '_last_name',
    )

    def __init__(self):
        self._user_name = None
        self._first_name = None
        self._last_name = None

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    #
    # user_name
    #
    @property
    def user_name(self):
        """ """
        return self._user_name

    def set_user_name(self, data):
        """Read-Only group metadata"""
        self._user_name = data

    #
    # first_name
    #
    @property
    def first_name(self):
        """ """
        return self._first_name

    def set_first_name(self, data):
        """Read-Write group metadata"""
        self._first_name = self._uni(data)

    #
    # last_name
    #
    @property
    def last_name(self):
        """ """
        return self._last_name

    def set_last_name(self, data):
        """ """
        self._last_name = self._uni(data)

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Owner Members Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Members')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('user_name', self.user_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('first_name', self.first_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('last_name', self.last_name))

        return printable_string


"""
{
    "status": "Success",
    "data": {
        "user": [
            {
                "userName": "38913025228917344202",
                "firstName": "python",
                "lastName": "sdk"
            },
            {
                "userName": "50162275934080584135",
                "firstName": "MISP",
                "lastName": "Integration"
            },
            {
                "userName": "58922734657784046384",
                "firstName": "Splunk",
                "lastName": "App"
            },
            {
                "userName": "73639540579427918388",
                "firstName": "Intel471",
                "lastName": "Feed"
            },
            {
                "userName": "bsummers",
                "firstName": "Bracey",
                "lastName": "Summers"
            }
        ]
    }
}
"""