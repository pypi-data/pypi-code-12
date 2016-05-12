# This file is part of the Online Services test tools
#
# Copyright 2015, 2016 Canonical Ltd.
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
import os
import unittest
import sys
try:
    from cStringIO import StringIO
except:
    from io import StringIO

from olstests import (
    assertions,
    fixtures,
    results,
    runners,
    scenarii,
    suites,
)


load_tests = scenarii.load_tests_with_scenarios


class TestSuiteSetup(unittest.TestCase):

    scenarios = [('unittest', dict(case_maker=fixtures.make_case)),
                 ('testtools', dict(case_maker=fixtures.make_testtools_case))]

    def run_suite(self, suite):
        res = results.TextResult(StringIO(), verbosity=0)
        res.startTestRun()
        suite.run(res)
        res.stopTestRun()
        return res

    def test_setup_pass(self):
        self.setup_called = False

        class Suite(suites.TestSuite):

            def setUp(inner):
                super(Suite, inner).setUp()
                self.setup_called = True

        suite = fixtures.make_suite(['pass', 'pass'], suite_maker=Suite)
        res = self.run_suite(suite)
        self.assertTrue(self.setup_called)
        self.assertTrue(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))

    def test_setup_errors(self):
        self.setup_called = False

        class Suite(suites.TestSuite):

            def setUp(inner):
                super(Suite, inner).setUp()
                self.setup_called = True
                raise AssertionError

        suite = fixtures.make_suite(['pass', 'pass'], suite_maker=Suite)
        res = self.run_suite(suite)
        # An error during the setup fails the run without running the tests
        self.assertTrue(self.setup_called)
        self.assertFalse(res.wasSuccessful())
        self.assertEqual(0, res.testsRun)
        self.assertEqual(1, len(res.errors))
        self.assertEqual(0, len(res.failures))
        self.assertEqual(
            'olstests.tests.test_suites.Suite({:x})'.format(id(suite)),
            res.errors[0][0].id())

    def test_tests_pass(self):
        self.setup_called = False
        self.cleanup_called = False

        class Suite(suites.TestSuite):

            def setUp(inner):
                super(Suite, inner).setUp()
                self.setup_called = True

                def cleanup():
                    self.cleanup_called = True
                inner.addCleanup(cleanup)

        suite = fixtures.make_suite(['pass', 'pass'], suite_maker=Suite)
        res = self.run_suite(suite)
        # When the tests pass, setup and cleanups are called.
        self.assertTrue(self.setup_called)
        self.assertTrue(self.cleanup_called)
        self.assertTrue(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        self.assertEqual(0, len(res.errors))
        self.assertEqual(0, len(res.failures))

    def test_tests_errors(self):
        self.setup_called = False
        self.cleanup_called = False

        class Suite(suites.TestSuite):

            def setUp(inner):
                super(Suite, inner).setUp()
                self.setup_called = True

                def cleanup():
                    self.cleanup_called = True
                inner.addCleanup(cleanup)

        suite = fixtures.make_suite(['pass', 'error'], suite_maker=Suite)
        res = self.run_suite(suite)
        # If a test fails, the cleanups are called
        self.assertTrue(self.setup_called)
        self.assertTrue(self.cleanup_called)
        self.assertFalse(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        self.assertEqual(1, len(res.errors))
        self.assertEqual(0, len(res.failures))

    def test_cleanup_errors(self):
        class Suite(suites.TestSuite):

            def setUp(inner):
                super(Suite, inner).setUp()

                def cleanup():
                    raise AssertionError
                inner.addCleanup(cleanup)

        suite = fixtures.make_suite(['pass', 'pass'], suite_maker=Suite)
        res = self.run_suite(suite)
        # If a cleanup fails, the suite fails even if the tests succeed
        self.assertFalse(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        self.assertEqual(1, len(res.errors))
        self.assertEqual(0, len(res.failures))
        self.assertEqual(
            'olstests.tests.test_suites.Suite({:x})'.format(id(suite)),
            res.errors[0][0].id())

invocation_path = None


class TestingSubprocessSuiteWithLoadFile(suites.SubprocessedSuiteWithLoadFile):

    def setUp(self):
        super(TestingSubprocessSuiteWithLoadFile, self).setUp()
        fixtures.override_env(self, 'OLSSELFTESTS_IN_SUBPROCESS', '1')
        # Make sure we call the right top-level script
        self.cmd = [sys.executable, invocation_path,
                    '--module=olstests',
                    '--format=subunit', '--load', self.test_list_path]


class TestForSubprocess(unittest.TestCase):
    """Special tests for subprocesses.

    We need failing and erroring tests in subprocesses for
    TestRunTestsConcurrent but we want them to succeed otherwise.

    We can't use the usual tests in fixtures because those are not loaded and
    as such can't be used with --load.

    Not all subprocess tests can rely on --load either.

    If you need to update this comment, time has come to re-think all the use
    cases and probably create a python file on the fly with whatever test is
    needed.
    """

    @staticmethod
    def make_suite(kinds):
        return fixtures.make_suite(
            kinds, lambda kind: TestForSubprocess('test_{}'.format(kind)))

    def test_pass(self):
        pass

    def test_fail(self):
        if os.environ.get('OLSSELFTESTS_IN_SUBPROCESS', False):
            raise self.failureException

    def test_error(self):
        if os.environ.get('OLSSELFTESTS_IN_SUBPROCESS', False):
            raise SyntaxError('invalid syntax')


class TestRunTestsConcurrent(unittest.TestCase):

    scenarios = [
        ('fork', dict(suite_class=suites.ForkedSuite,
                      suite_maker=fixtures.make_suite)),
        ('subproc', dict(suite_class=TestingSubprocessSuiteWithLoadFile,
                         suite_maker=TestForSubprocess.make_suite)),
    ]

    def setUp(self):
        super(TestRunTestsConcurrent, self).setUp()
        # Save the invocation path for tests that needs it
        global invocation_path
        invocation_path = os.path.realpath(sys.argv[0])
        # Some tests will create files (test list), guard against collisions
        fixtures.set_uniq_cwd(self)

    def run_suite(self, suite):
        res = results.TextResult(StringIO(), verbosity=0)
        # Run tests across 2 processes, it's enough to validate that the
        # plumbing is right between the main process and the subprocesses.
        runners.run_tests(suite, res, 2, split_suite=self.suite_class)
        return res

    def test_pass(self):
        res = self.run_suite(self.suite_maker(['pass', 'pass']))
        self.assertTrue(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        assertions.assertLength(self, 0, res.errors)
        assertions.assertLength(self, 0, res.failures)

    def test_fail(self):
        res = self.run_suite(self.suite_maker(['pass', 'fail']))
        self.assertFalse(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        assertions.assertLength(self, 0, res.errors)
        assertions.assertLength(self, 1, res.failures)

    def test_error(self):
        res = self.run_suite(self.suite_maker(['error', 'fail']))
        self.assertFalse(res.wasSuccessful())
        self.assertEqual(2, res.testsRun)
        assertions.assertLength(self, 0, res.errors)
        assertions.assertLength(self, 2, res.failures)


class TestingPickedSuite(suites.SubprocessedSuite):

    def setUp(self):
        super(TestingPickedSuite, self).setUp()
        fixtures.override_env(self, 'OLSSELFTESTS_IN_SUBPROCESS', '1')
        # Make sure we call the right top-level script
        self.cmd = [sys.executable, sys.argv[0],
                    '--module=olstests',
                    '--format=subunit',
                    '--pick', '{}/{}'.format(self.unique, self.factor),
                    # Restrict to the class we're testing so we don't recurse
                    TestForSubprocess.__name__]


class TestRunTestsConcurrentPicked(unittest.TestCase):
    """We can't reuse the tests from TestRunTestsConcurrent as they create test
    lists and --pick is aimed at avoiding test lists.

    """

    suite_class = TestingPickedSuite

    def run_suite(self, suite):
        res = results.TextResult(StringIO(), verbosity=0)
        # Run tests across 3 processes (because there are 3 tests ;) to
        # validate that the plumbing is right between the main process and the
        # subprocesses.
        runners.run_tests(suite, res, 3, split_suite=self.suite_class)
        res.stopTestRun()
        return res

    def test_them_all(self):
        # the subprocesses won't see the suite so we may as well provide an
        # empty one
        res = self.run_suite(fixtures.make_suite([]))
        self.assertFalse(res.wasSuccessful())
        self.assertEqual(3, res.testsRun)
        # testtools streams merge errors and failures
        assertions.assertLength(self, 0, res.errors)
        assertions.assertLength(self, 2, res.failures)


class TestRunSuiteForked(unittest.TestCase):

    def test_fork_fails(self):

        def failing_fork():
            raise OSError('os.fork() failed')

        fixtures.patch(self, os, 'fork', failing_fork)
        with self.assertRaises(OSError) as cm:
            suite = suites.ForkedSuite(unittest.TestSuite(), 0, 0)
            suite.run(results.TextResult(StringIO()))
        self.assertEqual('os.fork() failed', '{}'.format(cm.exception))

# MISSING tests: ForkedSuite, and SubprocessedSuite as well, should be tested
# without involving split_suite_for(). I.e. both parts of the subunit
# communication should be tested independently (which may be a hint that the
# current implementation is still not testable enough) -- vila 2015-12-04
