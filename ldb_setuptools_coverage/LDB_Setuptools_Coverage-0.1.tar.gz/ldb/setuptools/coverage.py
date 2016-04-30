# Copyright 2016 Alex Orange
# 
# This file is part of LDB Setuptools Coverage.
# 
# LDB Setuptools Coverage is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LDB Setuptools Coverage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with LDB Setuptools Coverage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import setuptools.command.test
from setuptools.compat import PY3
from setuptools.py31compat import unittest_main

import coverage
import coverage.report

import unittest
import sys


class CoverageTestCase(unittest.TestCase):
    def __init__(self, coverage_report):
        super(CoverageTestCase, self).__init__('test_coverage')
        self.coverage_report = coverage_report

    def test_coverage(self):
        self.assertTrue(self.coverage_report.is_all_covered())


class FullCoverageReport(coverage.report.Reporter):
    coverage_failure = False

    def report_fn(self, fn, an):
        num, den = an.numbers.ratio_covered
        self.coverage_failure |= num != den

    def is_all_covered(self):
        self.report_files(self.report_fn, None)
        return not self.coverage_failure


class CoverageTestRunner(object):
    def __init__(self, inner_runner, packages):
        if inner_runner is None:
            inner_runner = unittest.TextTestRunner()
        self.inner_runner = inner_runner
        self.packages = packages

    def run(self, test):
        def coverage_test(result):
            cov = coverage.Coverage(source=self.packages)
            cov.start()

            test(result)

            cov.stop()
            cov.save()
            cov.html_report()

            reporter = FullCoverageReport(cov, cov.config)
            coverage_test_case = CoverageTestCase(reporter)

            coverage_test_case(result)

        return self.inner_runner.run(coverage_test)


class CoverageCommand(setuptools.command.test.test, object):
    """Command to run unit tests after in-place build with coverage"""

    description = "run unit tests as with test command does but with coverage"

    def finalize_options(self):
        super(CoverageCommand, self).finalize_options()
        self.packages = self.distribution.packages

    def run_tests(self):
        # Purge modules under test from sys.modules. The test loader will
        # re-import them from the build location. Required when 2to3 is used
        # with namespace packages.
        if PY3 and getattr(self.distribution, 'use_2to3', False):
            module = self.test_args[-1].split('.')[0]
            if module in _namespace_packages:
                del_modules = []
                if module in sys.modules:
                    del_modules.append(module)
                module += '.'
                for name in sys.modules:
                    if name.startswith(module):
                        del_modules.append(name)
                list(map(sys.modules.__delitem__, del_modules))

        cov = coverage.Coverage(source=self.packages)
        cov.start()

        test_program = unittest_main(
            None, None, [unittest.__file__] + self.test_args,
            testLoader=self._resolve_as_ep(self.test_loader),
            testRunner=self._resolve_as_ep(self.test_runner),
            exit=False,
        )

        if not test_program.result.wasSuccessful():
            sys.stderr.write("ERROR: Tests failed!\n")
            sys.exit(1)

        cov.stop()
        cov.save()
        cov.html_report()

        reporter = FullCoverageReport(cov, cov.config)
        if not reporter.is_all_covered():
            cov.report(skip_covered=True)
            sys.stderr.write("ERROR: Coverage failed!\n")
            sys.exit(2)

        print "SUCCESS: Both testing and coverage passed!"
