# This file is part of the Online Services test tools
#
# Copyright 2014, 2015 Canonical Ltd.
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

import os
import sys
import unittest

import olstests
from olstests import (
    features,
    fixtures,
    styles,
    tests,
)


if sys.version_info >= (3,):
    unicode = str


@features.requires(tests.minimal_pep8)
class TestTestPep8Usage(unittest.TestCase):

    def test_no_packages(self):
        with self.assertRaises(AssertionError) as cm:

            class Pep8(styles.TestPep8):

                packages = []

            test = Pep8('test_pep8_conformance')
            test.test_pep8_conformance()

        if sys.version_info < (3,):
            self.assertEqual('You should define some packages to check',
                             unicode(cm.exception))
        else:
            self.assertEqual(
                '[] == [] : You should define some packages to check',
                str(cm.exception))


@features.requires(tests.minimal_pyflakes)
class TestTestPyflakesUsage(unittest.TestCase):

    def test_no_packages(self):
        with self.assertRaises(AssertionError) as cm:

            class Pyflakes(styles.TestPyflakes):

                packages = []

            test = Pyflakes('test_pyflakes_conformance')
            test.test_pyflakes_conformance()

        if sys.version_info < (3,):
            self.assertEqual('You should define some packages to check',
                             unicode(cm.exception))
        else:
            self.assertEqual(
                '[] == [] : You should define some packages to check',
                str(cm.exception))


class TestPythonWalker(unittest.TestCase):

    def setUp(self):
        super(TestPythonWalker, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_empty(self):
        pw = styles.PythonFileWalker('.')
        self.assertEqual([], list(pw.iter('')))

    def test_walk_from_root(self):
        fixtures.build_tree('''
file: foo.py
dir: a
# a/bar has no .py, it won't be selected
file: a/bar
file: a/bar.py
''')
        pw = styles.PythonFileWalker(os.getcwd())
        self.assertEquals(['a/bar.py', 'foo.py'],
                          list(pw.iter('')))

    def test_walk_from_dir_inside_root(self):
        fixtures.build_tree('''
file: foo.py
dir: a
file: a/bar.py
dir: a/b
file: a/b/baz.py
''')
        pw = styles.PythonFileWalker('a')
        self.assertEquals(['b/baz.py'],
                          list(pw.iter('b')))


class TestPyflakesCheckDir(unittest.TestCase):

    def setUp(self):
        super(TestPyflakesCheckDir, self).setUp()
        fixtures.set_uniq_cwd(self)
        self.paths = []

        def check_file(path, ignored):
            self.paths.append(path)

        self.check = check_file

    def assertPaths(self, expected, start='', excludes=None):
        walker = styles.PythonFileWalker('')
        if excludes is None:
            excludes = []
        styles.pyflakes_check_dir(walker, start,
                                  excludes, self.check, None)
        self.assertEqual(expected, self.paths)

    def test_empty(self):
        self.assertPaths([], '')

    def test_tree(self):
        fixtures.build_tree('''
file: foo
file: foo.py
dir: a
file: a/bar
file: a/bar.py
dir: b
dir: b/c
file: b/c/baz.py
''')
        self.assertPaths(['a/bar.py', 'b/c/baz.py', 'foo.py'], )

    def test_tree_with_excludes(self):
        fixtures.build_tree('''
file: foo
file: foo.py
dir: a
file: a/bar
file: a/bar.py
dir: b
dir: b/c
file: b/c/baz.py
''')
        self.assertPaths(['a/bar.py', 'b/c/baz.py'], excludes=['foo.py'])

    def test_tree_with_excludes_in_dir(self):
        fixtures.build_tree('''
file: foo
file: foo.py
dir: a
file: a/bar
file: a/bar.py
file: a/baz.py
dir: b
dir: b/c
file: b/c/baz.py
''')
        self.assertPaths(['a/baz.py'], start='a', excludes=['a/bar.py'])


# Style tests for olstests itself


class TestPep8(styles.TestPep8):

    packages = [olstests]


class TestPyflakes(styles.TestPyflakes):

    packages = [olstests]
