# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from SiQt.siqt.dep_resolv import check_depflags

def assert_equal(a, b):
    assert a==b


def test_check_depflags():
    dep_flags = {'a': True, 'b': False, 'c': True, 'd': False}
    yield assert_equal, check_depflags(dep_flags, ['a', 'c']), True
    yield assert_equal, check_depflags(dep_flags, ['a', 'd']), False
    yield assert_equal, check_depflags(dep_flags, ['a', 'b', 'd']), False
    yield assert_equal, check_depflags(dep_flags, 'a'), True
    yield assert_equal, check_depflags(dep_flags, 'a and c'), True
    yield assert_equal, check_depflags(dep_flags, 'a and d'), False
    yield assert_equal, check_depflags(dep_flags, 'a and c and d'), False
    yield assert_equal, check_depflags(dep_flags, 'a or d'), True
    yield assert_equal, check_depflags(dep_flags, 'c and (a or d)'), True
    yield assert_equal, check_depflags(dep_flags, 'c and not d'), True
    yield assert_equal, check_depflags(dep_flags, '(c or d) and (not d or b)'), True







