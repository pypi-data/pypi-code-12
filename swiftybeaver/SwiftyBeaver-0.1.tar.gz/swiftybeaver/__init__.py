# -*- coding: utf-8 -*-

# The MIT License (MIT)
# https://opensource.org/licenses/MIT
#
# Copyright © 2016 Sebastian Kreutzberger, Steffen Ryll. Some Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Python implementation for SwiftyBeaver Cloud logging.

This module provides an easy-to-use logging handler for the SwiftyBeaver Cloud
Platform, which allows viewing logs in it's OS X app. To learn more about Swifty
Beaver, see https://github.com/SwiftyBeaver/SwiftyBeaver. Logs are transferred
AES-encrypted and, unless configured otherwise, not after every log event. The
details of this behaviour are explained in handler documentation.

Copyright © 2016 Sebastian Kreutzberger, Steffen Ryll. All Rights Reserved.
'''

__all__ = ['SwiftyBeaverAPI', 'SwiftyBeaverHandler']

__author__ = 'Steffen Ryll <steffen.ryll@gmx.de>'
__status__ = 'development'
__version__ = '0.1'
__date__ = '09 May 2016'


import base64
from functools import partial
import json
import logging
from random import SystemRandom
import string
from Crypto.Cipher import AES
from requests.auth import HTTPBasicAuth
from requests_futures.sessions import FuturesSession

logger = logging.Logger(__name__)


class SwiftyBeaverAPI():
    '''
    SwiftyBeaver Platform API wrapper.

    In order to successfully authenticate with the API, `app_id` and
    `app_secret` have to be provided during initialization. Additionally,
    `encryption_key` - the key used to encrypt the log entries - is required.

    To learn more about the API, see
    http://docs.swiftybeaver.com/article/15-api.

    ## Example Usage

    ### Posting Log Entries

    ```python
    > api = SwiftyBeaverAPI('hThdK', 'sdfa...s3mx', 'dsgb...ghdX')
    > api.post_entries(entries, device)
    ```

    ### Implementing a Callback

    ```python
    > def callback(response):
    >     print(response.status_code)
    >
    > api = SwiftyBeaverAPI('hThdK', 'sdfa...s3mx', 'dsgb...ghdX')
    > api.post_entries(entries, device, callback=callback)
    ```
    '''

    API_URL = 'https://api.swiftybeaver.com/api/{}/'
    BLOCK_SIZE = 16
    HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    def __init__(self, app_id, app_secret, encryption_key):
        '''
        Initialize the SwiftyBeaver Platform API.

        The arguments `app_id`, `app_secret`, and `encryption_key` are required
        and can be obtained using the SwiftyBeaver OS X app. They are used to
        authenticate with the Platform and for encrypting the log entries.
        '''

        self.auth = HTTPBasicAuth(app_id, app_secret)
        self.encryption_key = encryption_key

    def _generate_encryption_iv(self):
        '''Generate a random ascii key for encryption.'''

        get_character = partial(SystemRandom().choice, string.ascii_letters + string.digits)

        return ''.join(get_character() for _ in range(self.BLOCK_SIZE))

    def _pad_string(self, string):
        '''
        Right-pad a string according to PKCS #7.

        The length of the string output is divisible by the block size and the
        characteres needed to fill the remaining bytes each have the value of
        the remaining characteres' count.
        '''

        padding_length = 16 - (len(string) % 16)

        return string + chr(padding_length) * padding_length

    def encrypt_payload(self, payload):
        '''
        Encrypt payload data using AES CBC.

        The payload given will be encrypted using the encryption key given at
        initialization and a random ascii iv. If the payload is of type `dict`
        or `list` it will be converted to JSON prior to encryption.

        The iv concatenated with the base64-encoded, encrypted data will be
        returned as a string.
        '''

        if isinstance(payload, (dict, list,)):
            payload = json.dumps(payload)

        iv = self._generate_encryption_iv()
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(self._pad_string(payload))

        return iv + base64.b64encode(encrypted).decode('utf-8')

    def post(self, route, data=None, payload=None, callback=None):
        '''
        Post data or a payload to a specific route of the API.

        The payload will be encrypted and embedded in a JSON dict before the
        request. As the request is asynchronous, a callback that will be called
        with response object can be provided.
        '''

        def _callback(_, response):
            if callback is not None:
                callback(response)

        if payload is not None:
            data = {'payload': self.encrypt_payload(payload)}

        return FuturesSession().post(
            self.API_URL.format(route), auth=self.auth, json=data,
            headers=self.HEADERS, background_callback=_callback
        )

    def post_entries(self, entries, device, callback=None):
        '''
        Post log entries to the API.

        `entries`, a `list` containing single log records, and `device`, a
        `dict` with information about the current device are required. An
        optional callback may be provided as well.

        You can find out more about the required data structure at
        http://docs.swiftybeaver.com/article/18-sending-logs-via-api.
        '''

        assert entries and device, '`entries` and `device` must be set.'

        return self.post(
            'entries', payload={'entries': entries, 'device': device}, callback=callback
        )


class SwiftyBeaverHandler(logging.Handler):
    '''
    SwiftyBeaver Platform logging handler.

    This logging handler sends logging events to the SwiftyBeaver Cloud
    Platform, which allows for viewing logs in it's OS X app. To learn more
    about SwiftyBeaver, see https://github.com/SwiftyBeaver/SwiftyBeaver.

    In order to successfully authenticate with the API, `app_id` and
    `app_secret` have to be provided during initialization. Additionally,
    `encryption_key` - the key used to encrypt the log entries - is required.
    `device` is an optional `dict` that should conform to the specification at
    http://docs.swiftybeaver.com/article/18-sending-logs-via-api. If it is
    omitted, a mock device will be used.

    Please note that logs are transferred AES-encrypted and, unless configured
    otherwise, not after every log event. Each log record is associated with a
    certain number of points, depending on the log level. Log records will then
    be sent if the collected points are at least `minimum_threshold`. This
    system is in playe in order to prevent to many API calls during a short
    time.

    ## Example Usage

    ```python
    > swifty_handler = SwiftyBeaverHandler('hThdK', 'sdfa...s3mx', 'dsgb...ghdX', device=device)
    >
    > logger = logging.Logger(__name__)
    > logger.addHandler(swifty_handler)
    >
    > logger.info('Does it work?')
    ```
    '''

    MOCK_DEVICE = {
        'appBuild': 42,
        'appVersion': '1.0.0',
        'deviceModel': 'Raspberry Pi',
        'deviceName': 'RasPy',
        'firstAppBuild': 42,
        'firstAppVersion': '1.0.0',
        'firstStart': 1461139881.595012,
        'hostName': 'raspy.local',
        'lastStart': 1462193372.294958,
        'os': 'pyOS',
        'osVersion': '4.2.0',
        'starts': 42,
        'userName': 'python@swiftybeaver.com',
        'uuid': 'C28D515A-0424-49FC-A8E2-065EE8CDA146'
    }
    POINTS_PER_LEVEL = {
        logging.NOTSET: 0,
        logging.DEBUG: 1,
        logging.INFO: 5,
        logging.WARNING: 8,
        logging.ERROR: 10,
        logging.CRITICAL: 10
    }

    def __init__(self, app_id, app_secret, encryption_key, device=None, minimum_threshold=10):
        '''
        Initialize the SwiftyBeaver Platform logging handler.

        The arguments `app_id`, `app_secret`, and `encryption_key` are required
        and can be obtained using the SwiftyBeaver OS X app. They are used to
        authenticate with the Platform and for encrypting the log entries.
        If no `device` is given mock data is used. `device` should be a `dict`
        that must contain the keys specified in
        http://docs.swiftybeaver.com/article/18-sending-logs-via-api.
        `minimum_threshold` defines the minimum points required before sending
        the logs. It defaults to `10`.
        '''

        # old-style super call for Python 2 compability
        super(SwiftyBeaverHandler, self).__init__()

        self.api = SwiftyBeaverAPI(app_id, app_secret, encryption_key)
        self.entries = []

        self.device = device if device is not None else self.MOCK_DEVICE
        self.minimum_threshold = minimum_threshold

    def emit(self, record):
        '''
        Handle a logging event.

        This method is invoked automatically by the Python logging framework. It
        adds the logging record to the handler's list and sends the data if
        `self.minimum_threshold` is reached.
        '''

        level = record.levelno // 10  # Python uses two digit log levels
        thread_description = '{} #{}'.format(record.threadName, record.thread).strip()
        self.entries.append({
            'fileName': record.filename,
            'function': record.funcName,
            'level': level,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': thread_description,
            'timestamp': record.created
        })

        if self.logging_points >= self.minimum_threshold:
            self.send_log_entries()

    @property
    def logging_points(self):
        '''Get sum of points for log records in current entries.'''

        # multiply by ten because Python uses two digit logging levels
        return sum(
            self.POINTS_PER_LEVEL.get(entry['level'] * 10, 0) for entry in self.entries
        )

    def send_log_entries(self):
        '''Send collected log entries to API.'''

        def callback(response):
            '''Clear current entries if successful.'''

            if response.status_code == 200:
                self.entries = []
                logger.debug('Sent log entries to server')
            else:
                logger.error('Server responded with HTTP status {}'.format(response.status_code))

        return self.api.post_entries(self.entries, self.device, callback=callback)
