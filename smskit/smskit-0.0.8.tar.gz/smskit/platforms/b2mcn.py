"""
smskit.platforms.b2mcn
"""
import re
import io
import requests

from lxml import etree

from smskit.consts import PHONE_PATTERN

from smskit.platforms.base import BaseHandler


def get_tree(results):
    """Get tree."""
    xmltxt = results.content.strip()
    strtxt = io.BytesIO(xmltxt)

    tree = etree.parse(strtxt)    # pylint: disable=no-member
    message = tree.findtext('message')
    error = tree.findtext('error')
    return message, error


class B2mcnHandler(BaseHandler):
    """b2mcn Handler."""

    def __init__(self, **kwargs):
        self._config = kwargs.get('config', {})
        if ('CDKEY' or 'PASSWORD') not in self._config:
            raise KeyError('CDKEY和PASSWORD不能为空!')

        if ('REQUEST_URL' or 'QUERY_BALANCE_URL') not in self._config:
            raise KeyError('REQUEST_URL和QUERY_BALANCE_URL不能为空!')

    def send(self, phone, content):
        """Send sms."""
        if not re.match(PHONE_PATTERN, phone):
            return False, '手机号格式错误!'

        config = self._config

        params = {
            'phone': phone,
            'message': content,
            'cdkey': config.get('CDKEY'),
            'password': config.get('PASSWORD')
        }
        if 'ADDSERIAL' in self._config:
            params['addserial'] = self._config['ADDSERIAL']

        url = config['REQUEST_URL']
        results = requests.get(url, params=params)

        errmsg, code = get_tree(results)

        if code == '0':
            return True, errmsg
        else:
            return False, errmsg

    def query_balance(self, **kwargs):
        """Query balance."""
        config = self._config

        params = {
            'cdkey': config.get('CDKEY'),
            'password': config.get('PASSWORD')
        }
        url = config['QUERY_BALANCE_URL']
        results = requests.get(url, params=params)
        message, error = get_tree(results)

        return {'balance': message, 'status': error}
