"""
Test body filter
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import socket
from nose.tools import ok_, assert_raises
import email
import mock
from mailfilter import filters

def test10_positive_exact():
    """Positive for RBL"""
    imap = mock.Mock()
    tfilter = filters.RblFilter(imap, {'filter': 'rbl', 'org': 'spamcheck.swqzx', 'action': 'delete'}, {})
    message = email.message_from_file(open('test/rbl/spam.msg'))
    # Pretend gethostbyname HAS an entry about the IP in the mail
    with mock.patch('mailfilter.filters.gethostbyname', return_value='127.0.0.10') as f:
        ok_(not tfilter.check(1, '', message), 'RblFilter.check() failed')
        ok_(f.called, 'gethostbyname() never called')

def test20_negative_exact():
    """Negative for RBL"""
    imap = mock.Mock()
    tfilter = filters.RblFilter(imap, {'filter': 'rbl', 'org': 'spamcheck.plhb', 'action': 'delete'}, {})
    message = email.message_from_file(open('test/rbl/spam.msg'))
    # Pretend gethostbyname has no entry about the IP in the mail
    with mock.patch('mailfilter.filters.gethostbyname', side_effect=socket.gaierror) as f:
        ok_(tfilter.check(1, '', message), 'RblFilter.check() failed')
        ok_(f.called, 'gethostbyname() never called')
