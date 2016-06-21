# -*- coding: UTF-8 -*-
"""
Test header filter
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import io
from future import standard_library
standard_library.install_aliases()
from builtins import *
from nose.tools import ok_
import email
import mock
from mailfilter import filters
import pdb

def test10_positive_exact():
    """Positive for exact 'test mailing'"""
    imap = mock.Mock()
    tfilter = filters.HeaderFilter(imap, {'filter': 'header', 'part': 'subject', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/header/positive_exact.msg'))
    ok_(not tfilter.check(1, '', message), "HeaderFilter.check() failed")

def test11_positive__encoded_exact():
    """Positive for exact encoded from ''"""
    imap = mock.Mock()
    tfilter = filters.HeaderFilter(imap, {'filter': 'header', 'part': 'subject', 'check': "is 'Heizen Sie für immer gratis!'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/header/encoded.msg'))
    ok_(not tfilter.check(1, '', message), "HeaderFilter.check() failed")

def test20_negative_exact():
    """Negative for 'test  mailing'"""
    imap = mock.Mock()
    tfilter = filters.HeaderFilter(imap, {'filter': 'header', 'part': 'subject', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/header/positive_word.msg'))
    ok_(tfilter.check(1, '', message), "HeaderFilter.check() failed")

def test30_positive_upper():
    """Positive for 'TEST MAILING'"""
    imap = mock.Mock()
    tfilter = filters.HeaderFilter(imap, {'filter': 'header', 'part': 'subject', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/header/positive_upper.msg'))
    ok_(not tfilter.check(1, '', message), "HeaderFilter.check() failed")

def test40_positive_word():
    """Positive for 'test mailing'"""
    imap = mock.Mock()
    tfilter = filters.HeaderFilter(imap, {'filter': 'header', 'part': 'subject', 'check': "has test mailing", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/header/positive_word.msg'))
    ok_(not tfilter.check(1, '', message), "HeaderFilter.check() failed")

def test50_negative():
    """Negative for 'test mailing'"""
    imap = mock.Mock()
    tfilter = filters.HeaderFilter(imap, {'filter': 'header', 'part': 'subject', 'check': "has 'test mailing'", 'action': 'delete'}, {})
    message = email.message_from_file(open('test/header/negative.msg'))
    ok_(tfilter.check(1, '', message), "HeaderFilter.check() failed")
