# This file is part of the Online Services test tools
#
# Copyright 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest


from olstests import matchers


class TestNameMatcher(unittest.TestCase):

    def test_defaults(self):
        nm = matchers.NameMatcher()
        self.assertFalse(nm.matches(''))
        self.assertFalse(nm.matches('foo'))

    def test_simple_include(self):
        nm = matchers.NameMatcher(includes=['foo'])
        self.assertTrue(nm.matches('foo'))
        self.assertTrue(nm.matches('XXXfooXXX'))

    def test_multiple_includes(self):
        nm = matchers.NameMatcher(includes=['foo', '^bar'])
        self.assertTrue(nm.matches('foo'))
        self.assertTrue(nm.matches('bar'))
        self.assertTrue(nm.matches('barfoo'))
        self.assertTrue(nm.matches('foobar'))
        self.assertFalse(nm.matches('bazbar'))

    def test_simple_excludes(self):
        nm = matchers.NameMatcher(includes=['.*'], excludes=['foo'])
        self.assertTrue(nm.matches('bar'))
        self.assertFalse(nm.matches('foo'))
        self.assertFalse(nm.matches('foobar'))

    def test_multiple_excludes(self):
        nm = matchers.NameMatcher(includes=['.*'], excludes=['foo$', '^bar'])
        self.assertTrue(nm.matches('baz'))
        self.assertTrue(nm.matches('footix'))
        self.assertFalse(nm.matches('foo'))
        self.assertFalse(nm.matches('barista'))
