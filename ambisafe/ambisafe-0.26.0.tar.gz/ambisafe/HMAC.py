from base64 import b64encode
import calendar
from datetime import datetime
import hmac
from hashlib import sha512


def nonce():
    utctime = datetime.utcnow()
    return int(calendar.timegm(utctime.timetuple()) * 10 ** 3 + utctime.microsecond * 10 ** -3)


class HMAC(object):
    def __init__(self, secret, url, method, body=u'', nonce=None):
        self.secret = secret
        self.url = url
        self.method = method
        self.body = body if body else u''
        self._nonce = nonce
        self._signature = None

    @property
    def nonce(self):
        if not self._nonce:
            self._nonce = nonce()
        return self._nonce

    @property
    def signature(self):
        if not self._signature:
            message = u"{}\n{}\n{}\n{}".format(self.nonce, self.method, self.url, self.body)
            digest = hmac.new(self.secret, msg=message, digestmod=sha512)
            self._signature = b64encode(digest.digest()).replace(u'\n', u'')
        return self._signature
