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
import re
import unittest


from olstests import (
    assertions,
    filters,
    fixtures,
)


def create_tests_from_ids(ids):
    """Create TestCase objects from a list of ids (strings)."""
    suite = unittest.TestSuite()

    def test_id(name):
        return lambda: name

    for tid in ids:
        # We need an existing method to create a test. Arbitrarily, we use
        # id(), that souldn't fail ;) We won't run the test anyway.
        test = unittest.TestCase(methodName='id')
        # We can't define the lambda here or 'name' stay bound to the
        # variable instead of the value, use a proxy to capture the value.
        test.id = test_id(tid)
        suite.addTest(test)
    return suite


class TestFilterTestsById(unittest.TestCase):

    def assertFiltered(self, expected, condition, ids):
        """Check that ``condition`` filters tests created from ``ids``."""
        filtered = filters.filter_suite(condition, create_tests_from_ids(ids))
        self.assertEqual(expected, [t.id() for t in filtered])

    def test_filter_none(self):
        test_names = ['foo', 'bar']
        self.assertFiltered(test_names, lambda t: True, test_names)

    def test_filter_all(self):
        test_names = ['foo', 'bar']
        self.assertFiltered([], lambda t: False, test_names)

    def test_filter_start(self):
        self.assertFiltered(['foo', 'footix'],
                            lambda t: t.id().startswith('foo'),
                            ['foo', 'footix', 'bar', 'baz', 'fo'])

    def test_filter_in(self):
        self.assertFiltered(['bar', 'baz'],
                            lambda t: t.id() in ('bar', 'baz'),
                            ['foo', 'footix', 'bar', 'baz', 'fo'])

    def test_filter_single(self):
        self.assertFiltered(['bar'],
                            lambda t: t.id() == 'bar',
                            ['foo', 'bar', 'baz'])

    def test_filter_regexp(self):
        ba = re.compile('ba')
        self.assertFiltered(['bar', 'baz', 'foobar'],
                            lambda t: bool(ba.search(t.id())),
                            ['foo', 'bar', 'baz', 'foobar', 'qux'])


class TestFilterTestsByRegexps(unittest.TestCase):

    def assertFiltered(self, expected, regexps, ids):
        """Check that ``regexps`` filters tests created from ``ids``."""
        filtered = filters.include_regexps(regexps, create_tests_from_ids(ids))
        self.assertEqual(expected, [t.id() for t in filtered])

    def test_filter_none(self):
        self.assertFiltered(['foo', 'bar'], [], ['foo', 'bar'])

    def test_filter_one_regexp(self):
        self.assertFiltered(['foo', 'foobar', 'barfoo'], ['.*foo.*'],
                            ['foo', 'foobar', 'barfoo', 'baz'])

    def test_filter_several_regexps(self):
        self.assertFiltered(['foo', 'foobar', 'barfoo'], ['foo', 'arf'],
                            ['foo', 'foobar', 'barfoo', 'baz'])

    def test_filter_unanchored(self):
        self.assertFiltered(['foo', 'foobar', 'barfoo', 'xfoox'], ['foo'],
                            ['foo', 'foobar', 'barfoo', 'baz', 'xfoox'])

    def test_filter_start(self):
        self.assertFiltered(['foo', 'foobar'], ['^foo'],
                            ['foo', 'foobar', 'barfoo', 'baz', 'xfoox'])

    def test_filter_ends(self):
        self.assertFiltered(['foo', 'barfoo'], ['foo$'],
                            ['foo', 'foobar', 'barfoo', 'baz', 'xfoox'])


class TestFilterTestsByExcludedPrefixes(unittest.TestCase):

    def assertFiltered(self, expected, regexps, ids):
        """Check that ``prefixes`` filters tests created from ``ids``."""
        filtered = filters.exclude_regexps(regexps,
                                           create_tests_from_ids(ids))
        self.assertEqual(expected, [t.id() for t in filtered])

    def test_no_excludes(self):
        self.assertFiltered(['foo', 'bar'], [], ['foo', 'bar'])

    def test_one_exclude(self):
        self.assertFiltered(['bar'], ['foo'],
                            ['foo.bar', 'bar', 'foo.baz'])

    def test_several_excludes(self):
        self.assertFiltered(['bar'], ['foo', 'bar.'],
                            ['foo.bar', 'bar', 'foo.baz', 'bar.baz'])


class TestIncludeList(unittest.TestCase):

    def assertFiltered(self, expected, test_names, ids):
        """Check that ``test_names`` filters tests created from ``ids``."""
        filtered = filters.include_id_list(
            test_names, create_tests_from_ids(ids))
        self.assertEqual(expected, [t.id() for t in filtered])

    def test_empty(self):
        self.assertFiltered([], [], ['fail', 'pass', 'skip'])

    def test_include_knowns(self):
        self.assertFiltered(['pass', 'skip'], ['pass', 'skip'],
                            ['fail', 'pass', 'skip'])

    def test_include_with_unknowns(self):
        self.assertFiltered(['pass'],
                            ['dont.exist', 'funny.one', 'pass'],
                            ['fail', 'pass', 'skip'])

    def test_respect_list_order(self):
        self.assertFiltered(['skip', 'pass'], ['skip', 'pass'],
                            ['fail', 'pass', 'skip'])

    def test_create_duplicates(self):
        self.assertFiltered(['pass', 'pass'], ['pass', 'pass'],
                            ['fail', 'pass', 'skip'])

    def test_keep_duplicates(self):
        self.assertFiltered(['pass'], ['pass'],
                            ['fail', 'pass', 'pass'])


class TestPick(unittest.TestCase):

    def assertFiltered(self, expected, rank, modulo, ids):
        """Check that ``part`` filters tests created from ``ids``."""
        filtered = filters.pick(create_tests_from_ids(ids), rank, modulo)
        self.assertEqual(expected, [t.id() for t in filtered])

    def test_no_ratio(self):
        self.assertFiltered(['fail', 'pass', 'skip'],
                            0, 0, ['fail', 'pass', 'skip'])

    def test_first_ratio(self):
        self.assertFiltered(['fail', 'skip'],
                            1, 2, ['fail', 'pass', 'skip'])

    def test_last_ratio(self):
        self.assertFiltered(['pass'],
                            2, 2, ['fail', 'pass', 'skip'])

    def test_bogus_ratio(self):
        self.assertFiltered([],
                            12, 8,
                            ['fail', 'pass', 'skip'])


class TestPartitionSuite(unittest.TestCase):

    def assertPartition(self, expected, count, ids):
        """Check how tests created from ``ids`` are partitioned."""
        suites = filters.partition_suite(create_tests_from_ids(ids), count)
        self.assertEqual(expected, [[t.id() for t in s] for s in suites])

    def test_empty(self):
        self.assertPartition([[]], 1, [])

    def test_single(self):
        self.assertPartition([['one']], 1, ['one'])

    def test_one_by_suite(self):
        self.assertPartition([['one'], ['two']], 2, ['one', 'two'])

    def test_two_by_suite(self):
        self.assertPartition([['one', 'three'], ['two', 'four']],
                             2, ['one', 'two', 'three', 'four'])


class TestLoadTestIdList(unittest.TestCase):

    def setUp(self):
        super(TestLoadTestIdList, self).setUp()
        fixtures.set_uniq_cwd(self)

    def _create_test_list_file(self, content):
        with io.open('tests.list', 'w', encoding='utf-8') as f:
            f.write(content)
        fr = io.open('tests.list', 'r', encoding='utf-8')
        self.addCleanup(fr.close)
        return fr

    def test_load_test_list(self):
        flist = self._create_test_list_file('mod1.cl1.meth1\nmod2.cl2.meth2\n')
        tlist = filters.load_test_id_list(flist)
        assertions.assertLength(self, 2, tlist)
        self.assertEqual('mod1.cl1.meth1', tlist[0])
        self.assertEqual('mod2.cl2.meth2', tlist[1])

    def test_load_dirty_file(self):
        flist = self._create_test_list_file(
            '  mod1.cl1.meth1\n\nmod2.cl2.meth2  \nbar baz\n')
        tlist = filters.load_test_id_list(flist)
        assertions.assertLength(self, 4, tlist)
        self.assertEqual('mod1.cl1.meth1', tlist[0])
        self.assertEqual('', tlist[1])
        self.assertEqual('mod2.cl2.meth2', tlist[2])
        self.assertEqual('bar baz', tlist[3])
