#!/usr/bin/env python
import json
import re

from sys import version_info

if version_info < (3, 0):
    from urllib2 import HTTPError, URLError
    from urllib2 import urlopen
else:
    import ssl
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen


class NoLicenseNumber(Exception):
    pass


class NoLicenseNumberDataFound(Exception):
    pass


class InvalidLicenseNumber(Exception):
    pass


class UnexpectedResponse(Exception):
    pass


class LicenseNumber(object):

    RDW_URL = "https://api.datamarket.azure.com/opendata.rdw/" \
              "VRTG.Open.Data/v1/KENT_VRTG_O_DAT('%s')?$format=json"

    REGEXES = {
        1: "^[a-zA-Z]{2}[\d]{2}[\d]{2}$",  # XX-99-99
        2: "^[\d]{2}[\d]{2}[a-zA-Z]{2}$",  # 99-99-XX
        3: "^[\d]{2}[a-zA-Z]{2}[\d]{2}$",  # 99-XX-99
        4: "^[a-zA-Z]{2}[\d]{2}[a-zA-Z]{2}$",  # XX-99-XX
        5: "^[a-zA-Z]{2}[a-zA-Z]{2}[\d]{2}$",  # XX-XX-99
        6: "^[\d]{2}[a-zA-Z]{2}[a-zA-Z]{2}$",  # 99-XX-XX
        7: "^[\d]{2}[a-zA-Z]{3}[\d]{1}$",  # 99-XXX-9
        8: "^[\d]{1}[a-zA-Z]{3}[\d]{2}$",  # 9-XXX-99
        9: "^[a-zA-Z]{2}[\d]{3}[a-zA-Z]{1}$",  # XX-999-X
        10: "^[a-zA-Z]{1}[\d]{3}[a-zA-Z]{2}$",  # X-999-XX
        11: "^[a-zA-Z]{3}[\d]{2}[a-zA-Z]{1}$",  # XXX-99-X
        12: "^[a-zA-Z]{1}[\d]{2}[a-zA-Z]{3}$",  # X-99-XXX
        13: "^[\d]{1}[a-zA-Z]{2}[\d]{3}$",  # 9-XX-999
        14: "^[\d]{3}[a-zA-Z]{2}[\d]{1}$",  # 999-XX-9
        "CD": "^CD[ABFJNST][0-9]{1,3}$"  # CDB1 or CDJ45
    }

    FORMATS = {
        1: "%s%s-%s%s-%s%s",  # XX-99-99
        2: "%s%s-%s%s-%s%s",  # 99-99-XX
        3: "%s%s-%s%s-%s%s",  # 99-XX-99
        4: "%s%s-%s%s-%s%s",  # XX-99-XX
        5: "%s%s-%s%s-%s%s",  # XX-XX-99
        6: "%s%s-%s%s-%s%s",  # 99-XX-XX
        7: "%s%s-%s%s%s-%s",  # 99-XXX-9
        8: "%s-%s%s%s-%s%s",  # 9-XXX-99
        9: "%s%s-%s%s%s-%s",  # XX-999-X
        10: "%s-%s%s%s-%s%s",  # X-999-XX
        11: "%s%s%s-%s%s-%s",  # XXX-99-X
        12: "%s-%s%s-%s%s%s",  # X-99-XXX
        13: "%s-%s%s-%s%s%s",  # 9-XX-999
        14: "%s%s%s-%s%s-%s",  # 999-XX-9
        "CD": None  # CDB1 or CDJ45
    }

    def __init__(self, _license_number):
        self._raw_license_number = _license_number
        if not self.__validate():
            raise InvalidLicenseNumber()
        self._data = None

    def __validate(self):
        if not self.__get_type():
            return False
        return True

    def __get_type(self):
        for _key, _regex in self.REGEXES.items():
            match = re.match(_regex, self.stripped)
            if match is not None:
                return _key
        return False

    @property
    def stripped(self):
        """ Strips given license-number (removes dashes) """
        return self._raw_license_number.replace('-', '').strip().upper()

    @property
    def formatted(self):
        """ Return formatted license-number """
        _type = self.__get_type()
        if _type and self.FORMATS[_type] is not None:
            return self.FORMATS[_type] % tuple(self.stripped)
        return None

    @property
    def data(self):
        if self._data is None:
            self.__get_data()
        return self._data

    def __get_data(self):
        """ Request license-number data from RDW """
        if not self.__validate():
            raise InvalidLicenseNumber()

        try:
            if version_info < (3, 4):
                response = urlopen(self.RDW_URL % self.stripped)
            else:
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                response = urlopen(self.RDW_URL % self.stripped,
                    context=gcontext)
        except HTTPError as error:
            if error.code == 404:
                raise NoLicenseNumberDataFound()
            raise
        except URLError:
            # probably a connection refused error
            raise

        if response.code != 200:
            raise UnexpectedResponse()

        if 'json' not in response.info()['content-type']:
            raise UnexpectedResponse()

        raw_response = response.read().decode("utf-8")
        _results = json.loads(raw_response)
        self._data = _results['d']


if __name__ == "__main__":
    from sys import argv
    try:
        license_number = LicenseNumber(argv[1])
        print(license_number.data)
    except IndexError:
        raise NoLicenseNumber()
