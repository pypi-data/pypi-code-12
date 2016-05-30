"""
.. module:: python_xirsys.connection
   :synopsis: python-xirsys Connection Container

   See http://xirsys.com/api/

.. moduleauthor:: Alexander Kavanaugh (@kavdev)

"""

import requests

from .exceptions import XirSysAPIException

REST_ENDPOINT = "https://service.xirsys.com"


class Connection(object):

    def __init__(self, username, secret_key):
        self.url = REST_ENDPOINT
        self.username = username
        self.secret_key = secret_key

    def request(self, method, path, **kwargs):
        kwargs["ident"] = self.username
        kwargs["secret"] = self.secret_key

        # Remove None entries
        kwargs = {key: value for key, value in kwargs.items() if kwargs[key] is not None}

        # Coerce all kwargs to strings
        for key, value in kwargs.items():
            kwargs[key] = str(value)

        response = requests.request(method, url=self.url + path, data=kwargs).json()

        status_code = response["s"]
        error = response["e"]
        data = response["d"]

        if status_code == 200:
            return data
        else:
            raise XirSysAPIException("XirSys endpoint returned an HTTP {status}: {message}".format(status=status_code, message=error))

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
