# This file is part of the Online Services test tools
#
# Copyright 2013-2016 Canonical Ltd.
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

from __future__ import unicode_literals
import io
import unittest


import testtools


from olstests import (
    assertions,
    fixtures,
    results,
)


class TestTextResultOutput(unittest.TestCase):

    def assertOutput(self, expected, kind):
        test = fixtures.make_case(kind)
        out = io.StringIO()
        res = results.TextResult(out)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res.convert_delta_to_float = zero
        test.run(res)
        self.assertEqual(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('.', 'pass')

    def test_fail(self):
        self.assertOutput('F', 'fail')

    def test_error(self):
        self.assertOutput('E', 'error')

    def test_skip(self):
        self.assertOutput('s', 'skip')

    def test_skip_reason(self):
        self.assertOutput('s', 'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('x', 'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('u', 'unexpected_success')


def expand_template_for_test(template, test, kwargs=None):
    """Expand common references in template.

    Tests that check run outputs can be simplified if they use templates
    instead of litteral expected strings. There are plenty of examples below.

    :param template: A string where common strings have been replaced by a
        keyword so 1) tests are easier to read, 2) we don't run into pep8
        warnings for long lines.

    :param test: The test case under scrutiny.

    :param kwargs: A dict with more keywords for the template. This allows
        some tests to add more keywords when they are test specific.
    """
    if kwargs is None:
        kwargs = dict()

    def cleanup_file_name(name):
        # Getting the file name right is tricky, depending on whether the
        # module was just recompiled or not __file__ can be either .py or .pyc
        # but when it appears in an exception, the .py is always used.
        return name.replace('.pyc', '.py').replace('.pyo', '.py')

    filename = cleanup_file_name(__file__)
    traceback_fixed_length = kwargs.get('traceback_fixed_length', None)
    if traceback_fixed_length is not None:
        # We need to calculate the traceback detail length which includes the
        # file name.
        full_length = traceback_fixed_length + len(filename)
        # subunit prefixes the traceback with its length, this is the only
        # place that it can be properly calculated.
        kwargs['subunit_traceback_length'] = '%X' % (full_length,)
    traceback_line = getattr(test, 'traceback_line', None)
    kwargs['traceback_line'] = traceback_line
    traceback_file = getattr(test, 'traceback_file', None)
    kwargs['traceback_file'] = cleanup_file_name(traceback_file)
    # To allow easier reading for template, we format some known values
    kwargs.update(dict(classname='%s.%s' % (test.__class__.__module__,
                                            test.__class__.__name__),
                       name=test._testMethodName,
                       filename=filename))
    return template.format(**kwargs)


class TestVerboseResultOutput(unittest.TestCase):

    def assertOutput(self, template, kind):
        test = fixtures.make_case(kind)
        expected = expand_template_for_test(template, test)
        out = io.StringIO()
        res = results.TextResult(out, verbosity=2)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res.convert_delta_to_float = zero
        test.run(res)
        self.assertEqual(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('''\
{classname}.{name} ... OK (0.000 secs)
''',
                          'pass')

    def test_fail(self):
        self.assertOutput('''\
{classname}.{name} ... FAIL (0.000 secs)
''',
                          'fail')

    def test_error(self):
        self.assertOutput('''\
{classname}.{name} ... ERROR (0.000 secs)
''',
                          'error')

    def test_skip(self):
        self.assertOutput('''\
{classname}.{name} ... SKIP (0.000 secs)
''',
                          'skip')

    def test_skip_reason(self):
        self.assertOutput('''\
{classname}.{name} ... SKIP Reason (0.000 secs)
''',
                          'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('''\
{classname}.{name} ... XFAIL (0.000 secs)
''',
                          'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('''\
{classname}.{name} ... NOTOK (0.000 secs)
''',
                          'unexpected_success')


def summary_from_subunit(test, stream=None, noise=None):
    """Run a suite returning the summary from the subunit v2 stream."""
    if stream is None:
        stream = io.BytesIO()
    # Create the subunit v2 stream by running the test
    res = results.SubunitProducer(stream)
    test.run(res)
    # Now, process the subunit stream so we can assert about its content
    input_stream = io.BytesIO(stream.getvalue())
    subunit_case = results.SubunitConsumer(input_stream, noise)
    summary = testtools.StreamSummary()
    summary.startTestRun()
    subunit_case.run(summary)
    summary.stopTestRun()
    return summary


class TestSubunitSummaryForUnittest(unittest.TestCase):
    """Test subunit v2 output stream."""

    def run_case(self, kind):
        case = fixtures.make_case(kind)
        summary = summary_from_subunit(case)
        self.assertEqual(1, summary.testsRun)
        return summary

    def test_pass(self):
        summary = self.run_case('pass')
        self.assertTrue(summary.wasSuccessful())

    def test_fail(self):
        summary = self.run_case('fail')
        self.assertFalse(summary.wasSuccessful())
        # FIXME: Check with newer testtools, that should be summary.failures --
        # vila 2015-05-26
        assertions.assertLength(self, 1, summary.errors)

    def test_error(self):
        summary = self.run_case('error')
        self.assertFalse(summary.wasSuccessful())
        assertions.assertLength(self, 1, summary.errors)

    def test_skip(self):
        summary = self.run_case('skip')
        self.assertTrue(summary.wasSuccessful())
        assertions.assertLength(self, 1, summary.skipped)

    def test_skip_reason(self):
        summary = self.run_case('skip_reason')
        self.assertTrue(summary.wasSuccessful())
        assertions.assertLength(self, 1, summary.skipped)
        self.assertEqual('Reason', summary.skipped[0][1])

    def test_expected_failure(self):
        summary = self.run_case('expected_failure')
        self.assertTrue(summary.wasSuccessful())
        assertions.assertLength(self, 1, summary.expectedFailures)

    def test_unexpected_success(self):
        summary = self.run_case('unexpected_success')
        self.assertTrue(summary.wasSuccessful())
        assertions.assertLength(self, 1, summary.unexpectedSuccesses)


class SpuriousOutput(unittest.TestCase):
    """What happens to the output produced by tests.

    By default, subunit/testtools will swallow the spurious output mixed with
    the subunit stream.

    SubunitConsumer explicitly routes spurious output to a dedicated stream.
    """
    def test_spurious_output(self):
        stream = io.BytesIO()
        noise = io.BytesIO()

        class Test(unittest.TestCase):

            def test_spurious(self):
                stream.write('spurious\n'.encode('utf8'))

        summary = summary_from_subunit(Test('test_spurious'), stream, noise)
        self.assertTrue(summary.wasSuccessful())
        self.assertEqual('spurious\n', noise.getvalue().decode('utf8'))

# MISSING tests: StreamResult needs to be tested somewhere. We use it
# indirectly but it could be a pain to debug -- vila 2016-01-20
