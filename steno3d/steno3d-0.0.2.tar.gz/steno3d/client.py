"""clinet.py contains the functionality to link the python steno3d
client with the steno3d website
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from builtins import input

import keyring
import requests
from six import string_types
from six.moves.urllib.parse import urlparse
from time import sleep


PRODUCTION_BASE_URL = 'https://steno3d.com/'
API_SUBPATH = 'api/'
ACCEPTABLE_ACL_ERRORS = set(['repeated users', 'to delete'])
SLEEP_TIME = 0.1

WELCOME_HEADER = """

Welcome to the Python client library for Steno3D!

"""

DEVKEY_PROMPT = "If you have a Steno3D developer key, please enter it here > "

WELCOME_MESSAGE = """

If you do not have a Steno3D developer key, you need to request
one from the Steno3D website in order to access the API. Please
log in to the application (if necessary) and request a new key.

{base_url}settings/api

If you are not yet signed up, you can do that here:

{base_url}signup

When you are ready, please enter the key above, or reproduce this
prompt by calling steno3d.login().

"""

LOGIN_FAILED = """

Oh no! We could not log you in.

The API developer key that you provided could not be validated. You could:

1) Clear your keychain with `steno3d.logout()` and try again
2) Restart your Python kernel and try again
3) Check that you have the correct API key
4) Ask for <help@steno3d.com>
5) Open an issue https://github.com/3ptscience/steno3dpy/issues

"""

NOT_CONNECTED = """

Oh no! We could not connect to the Steno3D server.

Please ensure that you are:

1) connected to the Internet!
2) Can connect to Steno3D on  https://steno3d.com

If the issue persists please:

1) Ask for <help@steno3d.com>
2) Open an issue https://github.com/3ptscience/steno3dpy/issues

"""

BAD_API_KEY = """

The developer key should be 36 characters.
Please checkout the website for your key:

{base_url}settings/api

"""


class _Comms(object):
    """Comms controls the interaction between the python client and the
    steno3d website.
    """

    def __init__(self):
        self._user = None
        self._base_url = PRODUCTION_BASE_URL
        self._hard_devel_key = None

    @property
    def host(self):
        """hostname of url"""
        parseresult = urlparse(self.base_url)
        return parseresult.hostname

    @property
    def url(self):
        """url endpoint for uploading"""
        return self.base_url + API_SUBPATH

    @property
    def base_url(self):
        """base url endpoint for uploading"""
        return getattr(self, '_base_url', PRODUCTION_BASE_URL)

    @base_url.setter
    def base_url(self, value):
        assert isinstance(value, string_types), \
            'Endpoint path must be a string'
        # Patch '/' onto bare URL endpoints
        if not value[-1] == '/':
            value += '/'
        # Check for HTTPS
        parsed = urlparse(value)
        if '.com' in parsed.hostname and parsed.scheme != 'https':
            raise Exception('Live endpoints require HTTPS.')

        self._base_url = value

    @property
    def devel_key(self):
        """developer key acquired from steno3d.com"""
        self._user = None
        if getattr(self, '_hard_devel_key', None) is not None:
            return self._hard_devel_key

        key = keyring.get_password('steno3d', self.host)
        if key in {None, 'None'}:
            return None
        return str(key)

    @devel_key.setter
    def devel_key(self, value):
        if value is None:
            del self.devel_key
        else:
            keyring.set_password('steno3d', self.host, value)

    @devel_key.deleter
    def devel_key(self):
        try:
            keyring.delete_password('steno3d', self.host)
        except keyring.errors.PasswordDeleteError:
            # Happens when the key does not exist
            pass

    def login(self, devel_key=None, skip_keychain=False, endpoint=None):
        """Login to steno3d.com to allow uploading resources"""
        if endpoint is not None:
            self.base_url = str(endpoint)

        if devel_key is not None:
            if skip_keychain:
                self._hard_devel_key = devel_key
            else:
                self.devel_key = devel_key

        if self.devel_key is None:
            print(WELCOME_MESSAGE.format(base_url=self.base_url))
            try:
                devel_key = raw_input(WELCOME_HEADER + DEVKEY_PROMPT)
            except NameError:
                devel_key = input(WELCOME_HEADER + DEVKEY_PROMPT)
            if len(devel_key) is not 36:
                print(BAD_API_KEY.format(base_url=self.base_url))
                try:
                    devel_key = raw_input(DEVKEY_PROMPT)
                except NameError:
                    devel_key = input(DEVKEY_PROMPT)
            self.devel_key = devel_key

        if getattr(self, '_user', None) is None:
            try:
                resp = requests.get(
                    self.url + 'me',
                    headers={'sshKey': self.devel_key}
                )
            except requests.ConnectionError:
                raise Exception(NOT_CONNECTED)
            if resp.status_code is not 200:
                self.devel_key = None
                raise Exception(LOGIN_FAILED)
            self._user = resp.json()

        username = self._user['uid']
        print(
            'Welcome to Steno3D! You are logged in as @{name}'.format(
                name=username
            )
        )

    def logout(self):
        """Logout current user and remove api key from keyring"""
        self.devel_key = None


Comms = _Comms()


def pause():
    """Brief pause on localhost to simulate network delay"""
    if 'localhost' in Comms.url:
        sleep(SLEEP_TIME)


def post(url, data=None, files=None):
    """Send data and files to the steno3d online endpoint"""
    data = {} if data is None else data
    filedict = {}
    for filename in files:
        if hasattr(files[filename], 'dtype'):
            filedict[filename] = files[filename].file
            filedict[filename + 'Type'] = files[filename].dtype
        else:
            filedict[filename] = files[filename]
    req = requests.post(
        Comms.url + url,
        data=data,
        files=filedict,
        headers={'sshKey': Comms.devel_key}
    )
    for key in files:
        files[key].file.close()
    return req


def add_acl(resource, accessor, role):
    """Add permissions to an object's ACL"""
    long_uid = (
        accessor if isinstance(accessor, string_types)
        else accessor.long_uid
    )
    data = {
        'user': long_uid,
        'role': role,
    }
    pause()
    response = requests.post(
        resource.url_api + '/access',
        data=data,
        headers={'sshKey': Comms.devel_key}
    )
    return response


def add_view_permissions(resource, accessor):
    """Add view permissions to an object"""
    return add_acl(resource, accessor, 'view')


def add_edit_permissions(resource, accessor):
    """Add edit permissions to an object"""
    return add_acl(resource, accessor, 'edit')


def remove_permissions(resource, accessor):
    """Remove permissions from an object"""
    long_uid = (
        accessor if isinstance(accessor, string_types)
        else accessor.long_uid
    )
    response = requests.delete(
        resource.url_api + '/access/{0}'.format(long_uid),
        headers={'sshKey': Comms.devel_key}
    )
    return response


def check_acl_response(resp):
    """Check for 'acceptable' errors"""
    if resp.status_code == 200:
        return True
    respjson = resp.json()
    return 'reason' in respjson and \
        any(telltale in respjson['reason']
            for telltale in ACCEPTABLE_ACL_ERRORS)


def plot(url):
    """Return an IFrame plot"""
    from IPython.display import IFrame
    return IFrame(url, width='100%', height=500)
