# This file is part of the Online Services test tools
#
# Copyright 2013 Canonical Ltd.
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

from olstests import assertions


class TestAssertMultiLineAlmostEqual(unittest.TestCase):

    def check(self, expected, actual):
        assertions.assertMultiLineAlmostEqual(self, expected, actual)

    def test_empty(self):
        self.check('', '')

    def test_single_ellipsis_single_line(self):
        self.check('...', 'tagada')

    def test_single_ellipsis_multiple_lines(self):
        self.check('...', 'foo\nbar')

    def test_multiple_ellipsis_multiple_lines(self):
        self.check('...\n...', 'foo\nbar')

    def test_traceback(self):
        # One main target of the assertion is to be able to match tracebacks
        # without having to care about file names/lines.
        self.check('''Traceback (most recent call last):
  File ..., in expectFailure
    predicate(*args, **kwargs)
  File ..., in assertEqual
    self.assertThat(observed, matcher, message)
  File ..., in assertThat
    raise MismatchError(matchee, matcher, mismatch, verbose)
testtools.matchers._impl.MismatchError: 1 != 0
''',
                   # This is almost a real traceback but the file names have
                   # been shortened to silent pep8 warnings about long lines ;)
                   '''Traceback (most recent call last):
  File "testtools/testcase.py", line 441, in expectFailure
    predicate(*args, **kwargs)
  File "testtools/testcase.py", line 322, in assertEqual
    self.assertThat(observed, matcher, message)
  File "testtools/testcase.py", line 417, in assertThat
    raise MismatchError(matchee, matcher, mismatch, verbose)
testtools.matchers._impl.MismatchError: 1 != 0
''')


class TestAssertLength(unittest.TestCase):

    def test_assertLength_matches_empty(self):
        assertions.assertLength(self, 0, [])

    def test_assertLength_matches_nonempty(self):
        assertions.assertLength(self, 3, [1, 2, 3])

    def test_assertLength_fails_different(self):
        self.assertRaises(AssertionError, assertions.assertLength, self, 1, [])

    def test_assertLength_shows_sequence_in_failure(self):
        with self.assertRaises(AssertionError) as cm:
            assertions.assertLength(self, 2, [1, 2, 3])
        self.assertEqual('Incorrect length: wanted 2, got 3 for [1, 2, 3]',
                         cm.exception.args[0])
