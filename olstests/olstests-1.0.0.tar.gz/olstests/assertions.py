# This file is part of the Online Services test tools
#
# Copyright 2013, 2014 Canonical Ltd.
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
"""Assertions that can be used against any test case."""

# doctests ?? Nah, fear not, it's only to reuse OutputChecker which does a good
# job at fuzzy matching texts with ELLIPSIS.
import doctest
import unittest


def assertMultiLineAlmostEqual(test, expected, actual):
    """Assert that a template matches the actual output.

    Comparing multiple lines for strict equality can introduce strong
    constraints for little added value. There are cases where some part of the
    lines are not relevant to the test goal (dates, times, directories
    containing the file names compared are a few often encountered cases).

    This assertion provides a way to mark such parts in the expected string
    with ellipsis (...).

    :param test: The calling test.

    :param expected: The expected string, all ellipsis there won't produce
        differences during the comparison.

    :param actual: The actual string to compare against.
    """
    checker = doctest.OutputChecker()
    options = doctest.ELLIPSIS
    matching = checker.check_output(expected, actual, options)
    if not matching:
        # We can't use output_checker.output_difference() here because... the
        # API is broken ('expected' must be a doctest specific object of which
        # a 'want' attribute will be our 'expected' parameter). So we just
        # fallback to our assertMultilineEqual since we know there *are*
        # differences and the output should be decently readable.
        orig = test.maxDiff
        try:
            test.maxDiff = None
            test.assertMultiLineEqual(expected, actual)
        finally:
            test.maxDiff = orig


def assertLength(test, length, obj_with_len):
    """Assert that obj_with_len is of length length.

    This display 'obj_with_len' which is more helpful than just knowing that
    its expected length is wrong.
    """
    if len(obj_with_len) != length:
        test.fail('Incorrect length: wanted {}, got {}'
                  ' for {!r}'.format(length, len(obj_with_len), obj_with_len))


def assertSuccessfullTest(outer, inner):
    """Run a test and check it did so successfully.

    :param outer: The test making the assertion.

    :param inner: The test to run that should succeed.

    :return: The result object if the outer test want to do further checks.
    """
    result = unittest.TestResult()
    inner.run(result)
    outer.assertEqual(1, result.testsRun)
    outer.assertTrue(result.wasSuccessful())
    return result
