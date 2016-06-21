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
from nose.tools import ok_
import email
import mock
from mailfilter import filters

def test10_positive_exact():
    """Positive for has 'test mailing'"""
    imap = mock.Mock()
    tfilter = filters.BodyFilter(imap, {'filter': 'body', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/body/positive_exact.msg'))
    ok_(not tfilter.check(1, '', message), 'BodyFilter.check() failed')

def test20_negative_exact():
    """Negative has 'test  mailing'"""
    imap = mock.Mock()
    tfilter = filters.BodyFilter(imap, {'filter': 'body', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/body/positive_word.msg'))
    ok_(tfilter.check(1, '', message), 'BodyFilter.check() failed')

def test30_positive_upper():
    """Positive for 'TEST MAILING'"""
    imap = mock.Mock()
    tfilter = filters.BodyFilter(imap, {'filter': 'body', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/body/positive_upper.msg'))
    ok_(not tfilter.check(1, '', message), 'BodyFilter.check() failed')

def test40_positive_word():
    """Positive for 'test mailing'"""
    imap = mock.Mock()
    tfilter = filters.BodyFilter(imap, {'filter': 'body', 'check': "has test mailing", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/body/positive_word.msg'))
    ok_(not tfilter.check(1, '', message), 'BodyFilter.check() failed')

def test20_negative():
    """Negative for 'test mailing'"""
    imap = mock.Mock()
    tfilter = filters.BodyFilter(imap, {'filter': 'body', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/body/negative.msg'))
    ok_(tfilter.check(1, '', message), 'BodyFilter.check() failed')
