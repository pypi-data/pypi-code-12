# This file is part of the Online Services test tools
#
# Copyright 2013, 2014, 2015 Canonical Ltd.
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
import os
import sys
import unittest


import pep8


from olstests import (
    assertions,
    features,
    matchers,
    tests,
    walkers,
)


if sys.version_info >= (3,):
    unicode = str


if tests.minimal_pep8.available():
    BaseReport = pep8.BaseReport
else:
    BaseReport = object


class UnitTestReport(BaseReport):

    def __init__(self, options):
        super(UnitTestReport, self).__init__(options)
        self._fmt = pep8.REPORT_FORMAT.get(options.format.lower(),
                                           options.format)
        self._msgs = []

    def error(self, line_number, offset, text, check):
        """Report an error, according to options."""
        super(UnitTestReport, self).error(line_number, offset, text, check)
        self._msgs.append(self._fmt % {
            'path': self.filename,
            'row': self.line_offset + line_number, 'col': offset + 1,
            'code': text[:4], 'text': text[5:],
        })


@features.requires(tests.minimal_pep8)
class TestPep8(unittest.TestCase):
    """Base test class to check a list of python modules with pep8.

    :cvar packages: A list of modules defined by the daughter class. All python
        files below this module will be checked.
    """

    packages = []
    exclude = []

    def setUp(self):
        super(TestPep8, self).setUp()
        self.pep8style = pep8.StyleGuide(
            exclude=self.exclude,
            filename=['*.py'],
            show_source=True,
        )
        self.report = self.pep8style.init_report(UnitTestReport)

    def test_pep8_conformance(self):
        self.assertNotEqual([], self.packages,
                            'You should define some packages to check')
        for package in self.packages:
            self.pep8style.input_dir(os.path.dirname(package.__file__))
        self.assertEqual([], self.report._msgs,
                         '\n'.join(self.report._msgs))


@features.requires(tests.minimal_pyflakes)
class TestPyflakes(unittest.TestCase):
    """Base test class to check a list of python modules with pyflakes.

    :cvar packages: A list of modules defined by the daughter class. All python
        files below this module will be checked.

    :cvar excludes: A list of paths that should not be checked.
    """

    packages = []
    excludes = []

    def test_pyflakes_conformance(self):
        from pyflakes import (
            api,
            reporter,
        )
        self.assertNotEqual([], self.packages,
                            'You should define some packages to check')
        out = io.StringIO()
        err = io.StringIO()

        # Workaround a bug in pyflakes on vivid -- vila 2015-08-21
        # still there on wily -- vila 2015-12-04
        class Reporter(reporter.Reporter):

            def flake(self, message):
                self._stdout.write('{}'.format(message))
                self._stdout.write('\n')

        report = Reporter(out, err)
        paths = [os.path.dirname(p.__file__) for p in self.packages]

        walker = PythonFileWalker(None)
        for p in paths:
            root, base = os.path.split(p)
            sw = walker.SubWalker(root)
            pyflakes_check_dir(sw, base, self.excludes,
                               api.checkPath, report)
        out_val = out.getvalue()
        if out_val:
            assertions.assertMultiLineAlmostEqual(self, '', out_val)
        err_val = err.getvalue()
        if err_val:
            assertions.assertMultiLineAlmostEqual(self, '', err_val)


def PythonFileWalker(root):
    file_matcher = matchers.NameMatcher(includes=['^.*\.py$'])

    def rel_file_name(walker, dir_path, name):
        return os.path.join(dir_path, name)

    def recurse_for_files(walker, dir_path):
        # Recurse and yield all items below dir_path (dir_path itself is
        # not yielded)
        for item in walker.iter(dir_path):
            yield item

    walker = walkers.Walker(root, file_matcher=file_matcher,
                            sort_key=unicode,
                            file_handler=rel_file_name,
                            dir_handler=recurse_for_files)
    return walker


def pyflakes_check_dir(walker, dir_path, excludes, check, report):
    for file_path in walker.iter(dir_path):
        if file_path not in excludes:
            check(walker.join_root(file_path), report)
