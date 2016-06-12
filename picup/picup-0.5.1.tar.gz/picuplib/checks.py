# -*- coding:utf8 -*-
# ####################### BEGIN LICENSE BLOCK ########################
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ######################## END LICENSE BLOCK #########################
"""
module for some argument cheking
"""

from json import loads
from requests import head

from .exceptions import (MallformedResize, UnsupportedRotation,
                         UnsupportedFormat, UnkownError, ServerError,
                         EmptyResponse, PercentageOutOfRange)
from .globals import ALLOWED_ROTATION, USER_AGENT

import logging
LOGGER = logging.getLogger(__name__)


def check_rotation(rotation):
    """checks rotation parameter if illegal value raises exception"""

    if rotation not in ALLOWED_ROTATION:
        allowed_rotation = ', '.join(ALLOWED_ROTATION)
        raise UnsupportedRotation('Rotation %s is not allwoed. Allowed are %s'
                                  % (rotation, allowed_rotation))


def check_resize(resize):
    """checks resize parameter if illegal value raises exception"""
    if resize is None:
        return

    resize = resize.lower().strip()

    if 'x' in resize:
        tmp = resize.lower().split('x')
        tmp = [x.strip() for x in resize.split('x')]
        if len(tmp) == 2 and tmp[0].isdigit() and tmp[1].isdigit():
            return
    elif '%' in resize:
        tmp = resize.split('%')[0]
        if tmp.isnumeric():
            tmp = int(tmp)
            if 1 <= tmp <= 1000:
                return
            else:
                raise PercentageOutOfRange("percentage must be between 1 and 1000")

    raise MallformedResize('Resize value "%s" is mallformed. '
                           'Desired format is: {width}x{height} or {percentage}%%' % resize)


def check_noexif(noexif):
    """checks if noexif parameter is boolean"""
    if not isinstance(noexif, bool):
        raise TypeError('noexif must be boolean')


def check_callback(callback):
    """checks if callback is callable"""
    if not callable(callback) and callback is not None:
        raise TypeError('%s is not callable' % callback)


def check_response(response):
    """
    checks the response if the server returned an error raises an exception.
    """

    LOGGER.debug('Response string: "%s"', response.text)

    if not response.text or response.text == 'null':
        raise EmptyResponse()

    if response.status_code < 200 or response.status_code > 300:
        raise ServerError('API requests returned with error: %s'
                          % response.status_code)

    try:
        response_text = loads(response.text)
    except ValueError:
        raise ServerError('The API did not returned a JSON string.')

    if 'failure' in response_text:
        if response_text['failure'] == 'Falscher Dateityp':
            raise UnsupportedFormat('Please look at picflash.org '
                                    'witch formats are supported')
        else:
            raise UnkownError(response_text['failure'])


def check_if_redirect(url):
    """
    checks if server redirects url
    """
    response = head(url, headers={'User-Agent': USER_AGENT})
    if response.status_code >= 300 and response.status_code < 400:
        return response.headers['location']

    return None
