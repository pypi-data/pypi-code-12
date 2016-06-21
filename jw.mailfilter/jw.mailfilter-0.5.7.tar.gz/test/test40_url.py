"""
URL filter (spamvertized mail)
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import email
import logging

import mock
from nose.tools import ok_
from gevent import socket
from mailfilter import filters

logging.basicConfig(level=logging.DEBUG)

def test10_positive_url():
    """Positive for spam URL"""
    imap = mock.Mock()
    tfilter = filters.UrlFilter(imap, {'filter': 'url', 'action': 'delete'}, {})
    message = email.message_from_file(open('test/url/spam_positive.msg'))
    # Pretend gethostbyname HAS an entry about the IP in the mail
    with mock.patch('mailfilter.filters.gethostbyname', return_value='127.0.0.10') as f:
        logging.info('---')
        ok_(not tfilter.check(1, '', message), 'UrlFilter.check() failed')
        ok_(f.called, 'gethostbyname() never called')

def test20_negative_url():
    """Negative for spam URL"""
    imap = mock.Mock()
    tfilter = filters.UrlFilter(imap, {'filter': 'url', 'action': 'delete'}, {})
    message = email.message_from_file(open('test/url/spam_negative.msg'))
    # Pretend gethostbyname has no entry about the IP in the mail
    with mock.patch('mailfilter.filters.gethostbyname', side_effect=socket.gaierror) as f:
        ok_(tfilter.check(1, '', message), 'UrlFilter.check() failed')
        ok_(f.called, 'gethostbyname() never called')
