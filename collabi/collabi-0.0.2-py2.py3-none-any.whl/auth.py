"""Provides authentication callback for requests.
"""

from requests.auth import AuthBase

class Auth(AuthBase):
    def __init__(self, core):
        self._core = core
        super(Auth, self).__init__()

    def __call__(self, req):
        self._core.refresh()
        req.headers['Authorization'] = 'Bearer ' + self._core.access_token
        return req
