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
import sys
import unittest

import subunit
import testtools
from subunit import test_results as su_results
from testtools import testresult as tt_results


class TextResult(tt_results.TextTestResult):
    """A TestResult which outputs activity to a text stream."""

    def __init__(self, stream, failfast=False, verbosity=1):
        if testtools.__version__ >= (0, 9, 30):
            super(TextResult, self).__init__(stream, failfast)
        else:
            # Maintain compatibility with what is shipped on precise until we
            # switch to trusty. In the mean time, we just ignore --failfast :-/
            # -- vila 2014-01-28
            super(TextResult, self).__init__(stream)
        self.verbose = verbosity > 1
        # Output is delayed until 'stopTest' is called. This ensures the output
        # is produced from a single place at a precise point in time (they are
        # cases where addError is called multiple times and delaying the output
        # provides a more consistent behavior).
        self.delayed_output = ''

    def startTest(self, test):
        if self.verbose:
            if sys.version_info < (3,):
                test_id = test.id().decode('utf8')
            else:
                test_id = test.id()
            self.stream.write(test_id)
            self.stream.write(' ... ')
            self.stream.flush()
        self.start_time = self._now()
        super(TextResult, self).startTest(test)

    def convert_delta_to_float(self, a_timedelta):
        return (a_timedelta.days * 86400.0 + a_timedelta.seconds +
                a_timedelta.microseconds / 1000000.0)

    def stopTest(self, test):
        self.stream.write(self.delayed_output)
        self.delayed_output = ''
        if self.verbose:
            elapsed_time = self._now() - self.start_time
            self.stream.write(' (%.3f secs)\n'
                              % self.convert_delta_to_float(elapsed_time))
        self.stream.flush()
        super(TextResult, self).stopTest(test)

    def startTestRun(self):
        super(TextResult, self).startTestRun()
        # Activate signal handling so KeyboardInterrupt use the same internal
        # plumbing as failfast
        unittest.installHandler()
        unittest.registerResult(self)

    def stopTestRun(self):
        super(TextResult, self).stopTestRun()
        for reason, skipped in self.skip_reasons.items():
            if not reason:
                reason = 'No reason given'
            self.stream.write('{} skipped: {}\n'.format(
                len(skipped), reason))

    def addError(self, test, err=None, details=None):
        if self.verbose:
            self.delayed_output += 'ERROR'
        else:
            self.delayed_output += 'E'
        super(TextResult, self).addError(test, err, details)

    def addFailure(self, test, err=None, details=None):
        if self.verbose:
            self.delayed_output += 'FAIL'
        else:
            self.delayed_output += 'F'
        super(TextResult, self).addFailure(test, err, details)

    def addSkip(self, test, reason):
        if self.verbose:
            if not reason:
                reason_displayed = ''
            else:
                reason_displayed = ' ' + reason
            self.delayed_output += 'SKIP{}'.format(reason_displayed)
        else:
            self.delayed_output += 's'
        super(TextResult, self).addSkip(test, reason)

    def addSuccess(self, test, details=None):
        if self.verbose:
            self.delayed_output += 'OK'
        else:
            self.delayed_output += '.'
        super(TextResult, self).addSuccess(test, details)

    def addExpectedFailure(self, test, err=None):
        if self.verbose:
            self.delayed_output += 'XFAIL'
        else:
            self.delayed_output += 'x'
        super(TextResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        if self.verbose:
            self.delayed_output += 'NOTOK'
        else:
            self.delayed_output += 'u'
        super(TextResult, self).addUnexpectedSuccess(test)


class SubunitProducer(testtools.ExtendedToStreamDecorator):
    """A test result producing a subunit v2 stream.

    The subunit stream is produced from testtools stream result events.
    """

    def __init__(self, stream):
        streamer = subunit.StreamResultToBytes(stream)
        super(SubunitProducer, self).__init__(streamer)


class SubunitConsumer(object):
    """A test result consuming a subunit v2 stream.

    The subunit stream is turned into testtools stream result events.
    Non subunit output is routed independently.

    The object acts as a test case and run(final_result) needs to be called to
    process the events through ``final_result``.
    """

    def __init__(self, stream, noise=None):
        if noise is None:
            # Unless told otherwise, that's where the noise should end up.
            noise = sys.stdout
        self.stream = stream
        self.noise = noise

    def run(self, result):
        # The received stream will be split between the subunit data and the
        # noise
        router = testtools.StreamResultRouter(result)
        noise_consumer = su_results.CatFiles(self.noise)
        router.add_rule(noise_consumer, 'test_id', test_id=None)
        su_test = subunit.ByteStreamToStreamResult(
            self.stream, non_subunit_name='noise')
        return su_test.run(router)
