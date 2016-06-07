
import urllib2

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tracking')

class Statuses(object):
    DELIVERED, SENT, STORED, DELIVERING, RETURN_TO_SENDER, UNKNOWN = range(6)

class Courier(object):

    def __init__(self, tracknum):
        self.tracknum = tracknum
        self.tracking_page = self.get_tracking_page()

    @property
    def url(self):
        return self.tracking_url.format(tracknum=self.tracknum)

    def is_tracknum_valid(self):
        raise NotImplementedError()
    
    def is_extended(self):
        raise NotImplementedError()

    def get_tracking_page(self):
        """Returns string with content of tracking page"""
        request = urllib2.Request(self.url)
        # request.headers['Host'] = 'api.posta.sk'
        request.headers['Cookie'] = 'TS017b7dd0=01a27f45ea2ea121c1458696e787b7414a7413503b8586dcb2e2c8048b20085d882b210ac3'
        request.headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"
        request.headers['Connection'] = 'keep-alive'
        request.headers['Accept-Language'] = 'en-US,en;q=0.5'
        request.headers['Accept-Encoding'] = 'deflate'
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'

        response = urllib2.urlopen(request)
        # TODO!!
        # xxx: timeout, caching, debugging, encoding?...
        return response.read()  # decode utf8??

    def get_expiring_in_days(self):
        """Za kolik dni zasilka expiruje"""

        if self.get_expiration_date():
            diff = self.get_expiration_date() - date.today()

            return diff.days
        else:
            return None
