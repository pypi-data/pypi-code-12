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
import contextlib
import os
import unittest
import subprocess
import sys
import traceback

from olstests import (
    filters,
    results,
)


@contextlib.contextmanager
def catching_errors(test, result):
    """Wrap test execution catching exceptions.

    KeyboardInterrupt is re-raised, other exceptions are sent to 'result' as
    errors.

    :note: This looks like a convoluted way to call result.addError() (and it
        is) but it neatly implements the use case.
    """
    try:
        yield
    except KeyboardInterrupt:
        raise
    except:
        result.addError(test, sys.exc_info())
    return


class TestSuite(unittest.TestSuite):
    """A test suite providing setUp/addCleanup.

    ``setUp`` is called before the tests are run. If it fails, tests are not
    run. Added cleanups are always called whether or not a test or setUp
    failed.
    """

    # We fake the TestCase API (or mock the implementation details that
    # leak). It's a cheap price to be able to re-use result.addError() and all
    # good bits that comes with it.
    failureException = AssertionError

    def __init__(self, *args, **kwargs):
        super(TestSuite, self).__init__(*args, **kwargs)
        self._cleanups = []

    def id(self):
        cls = self.__class__
        # We need a unique name in case the same suite class is used several
        # times hence the id().
        return '{}.{}({:x})'.format(cls.__module__, cls.__name__, id(self))

    def run(self, result, debug=False):
        setup_done = False
        with catching_errors(self, result):
            self.setUp()
            setup_done = True
        try:
            if setup_done:
                super(TestSuite, self).run(result, debug)
        finally:
            while self._cleanups:
                cleanup, args, kwargs = self._cleanups.pop()
                with catching_errors(self, result):
                    cleanup(*args, **kwargs)

    def setUp(self):
        """Setup the test suite before running it."""
        pass

    def addCleanup(self, function, *args, **kwargs):
        """Add a cleanup function to be called after running.

        Functions added with addCleanup will be called in reverse order of
        adding after running the tests, or after setUp if setUp raises an
        exception.

        If a function added with addCleanup raises an exception, the error will
        be recorded as a test suite error, and the next cleanup will then be
        run.

        Cleanup functions are always called before a test suite finishes
        running, even if setUp is aborted by an exception.
        """
        self._cleanups.append((function, args, kwargs))


class WorkerSuite(TestSuite):
    """Suite used by workers implementing concurrent execution."""

    def __init__(self, suite, unique, factor):
        super(WorkerSuite, self).__init__()
        self.suite = suite
        self.unique = unique
        self.factor = factor
        self.stream = None


class ForkedSuite(WorkerSuite):

    def __init__(self, suite, unique, factor):
        super(ForkedSuite, self).__init__(suite, unique, factor)
        self.child_pid = None

    def run(self, result):
        read, write = os.pipe()
        self.child_pid = os.fork()
        if self.child_pid:
            os.close(write)
            self.stream = os.fdopen(read, 'rb', 0)
            try:
                self.run_parent(result)
            finally:
                os.waitpid(self.child_pid, 0)
        else:
            os.close(read)
            self.stream = os.fdopen(write, 'wb', 0)
            # Leave stderr and stdout open so we can see test noise but close
            # stdin so that the child goes away if it decides to read from
            # stdin (otherwise its a roulette to see what child actually gets
            # keystrokes for pdb etc).

            # FIXME: This can be useful to debug if a breakpoint is set in such
            # a way that a single process will reach it. As such, it should be
            # exposed, at least so that devs can toggle it easily.
            # -- vila 2015-12-04
            sys.stdin.close()
            self.run_child(result)

    def run_parent(self, result):
        # Collect the stream sent by the child
        consumer = results.SubunitConsumer(self.stream)
        consumer.run(result)

    def run_child(self, result):
        # Send a a subunit stream to the parent, the received result is
        # ignored, it's the parent result that matters.
        try:
            result = results.SubunitProducer(self.stream)
            self.suite.run(result)
        except:
            # MISSINGTEST: Completely uncovered scenario here as we used
            # subunit v1 before -- vila 2016-01-12

            # Try and report traceback on stream, but exit with error
            # even if stream couldn't be created or something else
            # goes wrong.  The traceback is formatted to a string and
            # written in one go to avoid interleaving lines from
            # multiple failing children.
            try:
                self.stream.write(traceback.format_exc())
            finally:
                os._exit(1)
        # We're done. We don't want the execution to continue in the caller.
        os._exit(0)


class SubprocessedSuite(WorkerSuite):

    def __init__(self, suite, unique, factor):
        super(SubprocessedSuite, self).__init__(suite, unique, factor)
        self.cmd = None

    def run(self, result, debug=False):
        setup_done = False
        with catching_errors(self, result):
            self.setUp()
            setup_done = True
        try:
            if setup_done:
                process = self.run_child(result)
                # Collect the stream sent by the child
                consumer = results.SubunitConsumer(process.stdout)
                consumer.run(result)
        finally:
            while self._cleanups:
                cleanup, args, kwargs = self._cleanups.pop()
                with catching_errors(self, result):
                    cleanup(*args, **kwargs)

    def run_child(self, result):
        # FIXME: A proper error should be reported if self.cmd is not
        # set -- vila 2015-12-09
        process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        self.addCleanup(os.waitpid, process.pid, 0)
        # Close process stdin to avoid confusion when mutiple processes are
        # involved
        process.stdin.close()
        return process


class SubprocessedSuiteWithLoadFile(SubprocessedSuite):

    def __init__(self, suite, unique, factor):
        super(SubprocessedSuiteWithLoadFile, self).__init__(
            suite, unique, factor)
        self.test_list_path = None

    def setUp(self):
        super(SubprocessedSuiteWithLoadFile, self).setUp()
        self.test_list_path = '{}.test-list'.format(self.unique)
        self.addCleanup(os.remove, self.test_list_path)
        with open(self.test_list_path, 'w') as tl:
            for t in filters.iter_flat(self.suite):
                tl.write('{}\n'.format(t.id()))
