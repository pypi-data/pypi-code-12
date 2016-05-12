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


from olstests import (
    fixtures,
    walkers,
)


if sys.version_info >= (3,):
    unicode = str


class TestPathFromRoot(unittest.TestCase):

    def test_just_root(self):
        w = walkers.Walker('.')
        self.assertEqual('.', w.join_root())

    def test_one_component(self):
        w = walkers.Walker('.')
        self.assertEqual('./foo', w.join_root('foo'))

    def test_several_components(self):
        w = walkers.Walker('.')
        self.assertEqual('./foo/bar', w.join_root('foo', 'bar'))

    def test_sub_walker_new_root(self):
        w = walkers.Walker('.')
        s = w.SubWalker('foo')
        # We respect the root as provided by the user (i.e. no leading '.'
        self.assertEqual('foo/bar/baz', s.join_root('bar', 'baz'))


class TestSortKey(unittest.TestCase):

    def test_no_key(self):
        w = walkers.Walker('.')
        names = ['bar', 'foo', 'baz']
        self.assertEqual(list(names), w.sort_names(list(names)))

    def test_unicode_key(self):
        w = walkers.Walker('.', sort_key=unicode)
        self.assertEqual(['bar', 'baz', 'foo'],
                         w.sort_names(['bar', 'foo', 'baz']))


class TestIter(unittest.TestCase):

    def setUp(self):
        super(TestIter, self).setUp()
        fixtures.set_uniq_cwd(self)
        fixtures.build_tree('''
file: foo
dir: b
file: b/a
file: b/b
dir: c
''')

    def test_do_nothing(self):
        w = walkers.Walker('.')
        self.assertEqual([], list(w.iter('.')))

    def test_get_files(self):

        def rel_path(walker, dir_path, name):
            # Return the relative path
            return os.path.join(dir_path, name)

        def recurse_for_files(walker, dir_path):
            # Recurse and yield all items
            for item in walker.iter(dir_path):
                yield item

        w = walkers.Walker('.',  sort_key=unicode, file_handler=rel_path,
                           dir_handler=recurse_for_files)

        self.assertEqual(
            ['./b/a', './b/b', './foo'],
            list(w.iter('.')))

    def test_get_dirs(self):

        def get_dirs(walker, dir_path):
            # Recurse and yield all items
            for item in walker.iter(dir_path):
                yield item
            # Yeild the dir itself
            yield dir_path

        w = walkers.Walker('.',  sort_key=unicode,
                           dir_handler=get_dirs)

        self.assertEqual(['./b', './c'], list(w.iter('.')))
