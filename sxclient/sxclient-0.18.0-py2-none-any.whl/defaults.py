'''
Variables controlling the library's behaviour.

Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.

'''

import re

DEFAULT_REQUEST_TIMEOUT = 10

VALID_ENCODED_KEY_LENGTH = 56
VALID_ENCODED_KEY_CHARACTERS = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789+/='
)
VALID_DECODED_KEY_LENGTH = 42

UUID_HEADER_PATTERN = re.compile(
    r'''
    (?<=\()                 # lookbehind an opening parenthesis
    [0-9a-fA-F]{8}-         # 4-hex octet ended with hyphen
    (?:[0-9a-fA-F]{4}-){3}  # three 2-hex octets ended with hyphens
    [0-9a-fA-F]{12}         # 6-hex octet
    (?=\))                  # lookahead a closing parenthesis
    ''',
    re.VERBOSE
)

FILTER_UUID_TO_NAME = {
    u'd5dbdf0afb174d1ba9ce4060317af5b5': u'zcomp',
    u'7e7b7a8fe294458aa2abed8944ffce5c': u'undelete',
    u'43122b8c56d146718500aa6831eb983c': u'attribs',
    u'15b0ac3c404f481ebc986598e4577bbd': u'aes256'
}
FILTER_NAME_TO_UUID = {
    value: key for key, value in FILTER_UUID_TO_NAME.iteritems()
}
CACHE_EXPIRATION = 300
DEFAULT_UPLOADER_BATCH_SIZE = 2**20*4
