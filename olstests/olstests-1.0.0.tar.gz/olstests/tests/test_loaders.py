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

import os
import unittest
import sys

from olstests import (
    assertions,
    filters,
    fixtures,
    loaders,
    matchers,
)


if sys.version_info >= (3,):
    unicode = str


class TestImportFromPath(unittest.TestCase):

    def setUp(self):
        super(TestImportFromPath, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()

    def test_invalid_path(self):
        with open('__init__.py', 'w') as f:
            f.write('')
        with self.assertRaises(TypeError) as cm:
            self.loader.importFromPath('.')
        if sys.version_info < (3,):
            self.assertEqual("relative imports require the 'package' argument",
                             unicode(cm.exception))
        else:
            self.assertEqual(
                "the 'package' argument is required to perform a relative "
                "import for '.'", str(cm.exception))

    def test_weird_path(self):
        d = './foo.bar/baz'
        os.makedirs(d)
        with open(os.path.join(d, '__init__.py'), 'w') as f:
            f.write('')
        with self.assertRaises(ImportError) as cm:
            self.loader.importFromPath(d)
        if sys.version_info < (3,):
            assertions.assertMultiLineAlmostEqual(self, '''\
Failed to import foo.bar.baz at ./foo.bar/baz:
Traceback (most recent call last):
  File "...", line ..., in importFromPath
    return importlib.import_module(mod_name)
  File "...", line ..., in import_module
    __import__(name)
ImportError: No module named foo.bar.baz
''',
                                                  unicode(cm.exception))
        else:
            assertions.assertMultiLineAlmostEqual(self, '''\
Failed to import foo.bar.baz at ./foo.bar/baz:
Traceback (most recent call last):
  File "...", line ..., in importFromPath
    return importlib.import_module(mod_name)
  File "...", line ..., in import_module
  ...
  ...
  ...
  ...
  ...
  ...
  ...
  ...
  ...
  ...
  ...
  ...
ImportError: No module named 'foo'
''',
                                                  str(cm.exception))

    def test_invalid_python_file(self):
        with open('foo.py', 'w') as f:
            f.write("I'm no python code")
        with self.assertRaises(SyntaxError):
            self.loader.importFromPath('./foo.py')

    def test_invalid_file(self):
        with open('foo', 'w') as f:
            f.write("I'm no python code and I'm not even pretending")
        with self.assertRaises(ImportError) as cm:
            self.loader.importFromPath('./foo')
        if sys.version_info < (3,):
            assertions.assertMultiLineAlmostEqual(self, '''\
Failed to import foo at ./foo:
Traceback (most recent call last):
  File "...", line ..., in importFromPath
    return importlib.import_module(mod_name)
  File "...", line ..., in import_module
    __import__(name)
ImportError: No module named foo
''',
                                                  unicode(cm.exception))
        else:
            assertions.assertMultiLineAlmostEqual(self, '''\
Failed to import foo at ./foo:
Traceback (most recent call last):
  File "...", line ..., in importFromPath
    return importlib.import_module(mod_name)
  File "...", line ..., in import_module
  ...
  ...
  ...
  ...
ImportError: No module named 'foo'
''',
                                                  unicode(cm.exception))

    def test_unknown_file(self):
        with self.assertRaises(ImportError) as cm:
            self.loader.importFromPath('./foo.py')
        if sys.version_info < (3,):
            assertions.assertMultiLineAlmostEqual(self, '''\
Failed to import foo at ./foo.py:
Traceback (most recent call last):
  File "...", line ..., in importFromPath
    return importlib.import_module(mod_name)
  File "...", line ..., in import_module
    __import__(name)
ImportError: No module named foo
''',
                                                  unicode(cm.exception))
        else:
            assertions.assertMultiLineAlmostEqual(self, '''\
Failed to import foo at ./foo.py:
Traceback (most recent call last):
  File "...", line ..., in importFromPath
    return importlib.import_module(mod_name)
  File "...", line ..., in import_module
  ...
  ...
  ...
  ...
ImportError: No module named 'foo'
''',
                                                  unicode(cm.exception))

    def test_valid_file(self):
        self.assertIs(None, sys.modules.get('foo', None))
        with open('foo.py', 'w') as f:
            f.write("a = 'bar'")
        self.loader.importFromPath('./foo.py')
        # We can't directly use 'foo.a' but the module has been imported
        self.assertEqual('bar', sys.modules['foo'].a)


class TestPackagePathFromName(unittest.TestCase):

    def setUp(self):
        super(TestPackagePathFromName, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader(root=self.uniq_dir)

    def test_simple_package_name(self):
        fixtures.build_tree('''\
dir: foo
file: foo/__init__.py
imported = True
''')
        sys_path_entry, rel_path = self.loader.packageSysPathFromName('foo')
        self.assertEqual(self.uniq_dir, sys_path_entry)
        self.assertEqual('foo', rel_path)
        self.assertTrue(sys.modules['foo'].imported)

    def test_dotted_package_name(self):
        fixtures.build_tree('''\
dir: foo
file: foo/__init__.py
dir: foo/bar
file: foo/bar/__init__.py
imported = True
''')
        sys_path_entry, rel_path = self.loader.packageSysPathFromName(
            'foo.bar')
        self.assertEqual(self.uniq_dir, sys_path_entry)
        self.assertEqual('foo/bar', rel_path)
        self.assertTrue(sys.modules['foo.bar'].imported)

    def test_failing_import(self):
        with self.assertRaises(ImportError) as cm:
            sys_path_entry, rel_path = self.loader.packageSysPathFromName(
                'foo')
        if sys.version_info < (3,):
            self.assertEqual('No module named foo', unicode(cm.exception))
        else:
            self.assertEqual("No module named 'foo'", str(cm.exception))


class TestSortNames(unittest.TestCase):
    """Smoke test the sortNames method."""

    def setUp(self):
        super(TestSortNames, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()

    def test_sort_empty(self):
        self.assertEqual([], self.loader.sortNames([]))

    def test_sort_names(self):
        self.assertEqual(['a', 'b'], self.loader.sortNames(['b', 'a']))


def assertTestsEqual(test, expected, actual):
    """Assert that a test [suite] is the expected one.

    :param expected: A flat list of tests.

    :param actual: A TestSuite. Since this is flattened, it can also be a
        single test or a list of tests.
    """
    test.assertEqual(list(filters.iter_flat(expected)),
                     list(filters.iter_flat(actual)))


def assertTestIDs(test, expected, actual):
    """Assert that the test ids are the expected ones.

    :param expected: A list of test ids.

    :param actual: A TestSuite. Since this is flattened, it can also be a
        single test or a list of tests.
    """
    test.assertEqual(expected, [t.id()
                                for t in list(filters.iter_flat(actual))])


class TestIterFlat(unittest.TestCase):
    """Test iter_flat through assertTestsEqual acting as a proxy.

    This keep the tests short while giving 'assertTestsEqual' examples.
    """

    def test_empty_lists(self):
        assertTestsEqual(self, [], [])

    def test_empty_suite(self):
        assertTestsEqual(self, [], unittest.TestSuite())

    def test_single_vs_single(self):
        test = fixtures.make_case()
        assertTestsEqual(self, test, test)

    def test_single_vs_list(self):
        test = fixtures.make_case()
        assertTestsEqual(self, test, [test])

    def test_list_vs_single(self):
        test = fixtures.make_case()
        assertTestsEqual(self, [test], test)

    def test_list_vs_list(self):
        test = fixtures.make_case()
        assertTestsEqual(self, [test], [test])

    def test_simple_suite(self):
        test = fixtures.make_case()
        assertTestsEqual(self, test, unittest.TestSuite([test]))

    def test_embedded_suite(self):
        test = fixtures.make_case()
        inner = unittest.TestSuite([test])
        middle = unittest.TestSuite([inner])
        assertTestsEqual(self, test, unittest.TestSuite([middle]))


class TestAssertTestIDs(unittest.TestCase):

    def test_single(self):
        assertTestIDs(self, ['olstests.fixtures.UnittestTest.test_pass'],
                      fixtures.make_case())

    def test_several(self):
        assertTestIDs(self, ['olstests.fixtures.UnittestTest.test_pass',
                             'olstests.fixtures.UnittestTest.test_pass'],
                      [fixtures.make_case(), fixtures.make_case()])


class TestLoadTestsFromFile(unittest.TestCase):

    def setUp(self):
        super(TestLoadTestsFromFile, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()

    def test_empty_file(self):
        pass

    def test_single_test(self):
        fixtures.build_tree('''file: test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
''')
        suite = self.loader.loadTestsFromFile('./test_foo.py')
        self.assertEqual(1, suite.countTestCases())

    def test_sorted_tests(self):
        fixtures.build_tree('''file: test_foo.py
import unittest

class TestB(unittest.TestCase):

    def test_me_1(self):
      self.assertTrue(True)

class TestC(TestB):

    def test_me_2(self):
      self.assertTrue(True)

class TestA(TestC):

    def test_me_3(self):
        self.assertFalse(False)
''')
        suite = self.loader.loadTestsFromFile('./test_foo.py')
        self.assertEqual(6, suite.countTestCases())
        self.assertEqual(['test_foo.TestA.test_me_1',
                          'test_foo.TestA.test_me_2',
                          'test_foo.TestA.test_me_3',
                          'test_foo.TestB.test_me_1',
                          'test_foo.TestC.test_me_1',
                          'test_foo.TestC.test_me_2'],
                         [t.id() for t in filters.iter_flat(suite)])


class TestLoadTestFromFiles(unittest.TestCase):

    def setUp(self):
        super(TestLoadTestFromFiles, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()

    def test_empty_list(self):
        fixtures.build_tree('''file: p.py
import unittest

class Test(unittest.TestCase):

    def test_pass(self):
        pass
''')
        assertTestsEqual(self, [], self.loader.loadTestsFromFiles('.', []))

    def test_single_file(self):
        fixtures.build_tree('''file: test.py
import unittest

class Test(unittest.TestCase):

    def test_pass(self):
        pass
''')
        assertTestIDs(self, ['test.Test.test_pass'],
                      self.loader.loadTestsFromFiles('.', ['test.py']))

    def test_several_files(self):
        fixtures.build_tree('''
file: test2.py
import unittest

class Test(unittest.TestCase):

    def test_pass(self):
        pass
file: test1.py
import unittest

class Test(unittest.TestCase):

    def test_pass(self):
        pass
''')
        assertTestIDs(
            self, ['test1.Test.test_pass', 'test2.Test.test_pass'],
            self.loader.loadTestsFromFiles('.', ['test1.py', 'test2.py']))

    def test_empty_dir(self):
        assertTestsEqual(self, [], self.loader.loadTestsFromFiles('.', []))


class TestLoadTestFromFiles_Matching(unittest.TestCase):

    def setUp(self):
        super(TestLoadTestFromFiles_Matching, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()
        # A simple tree fitting all tests. Pro: single context to think about,
        # smaller tests. Cons: shared resource, do not abuse. Specific test are
        # encouraged to enrich locally to suit their needs rather than pollute
        # the shared env.
        fixtures.build_tree('''
file: other.py
import unittest
class T(unittest.TestCase):
  def test_inc(self): pass
file: inc.py
import unittest
class T(unittest.TestCase):
  def test_inc(self): pass
file: exc.py
import unittest
class T(unittest.TestCase):
  def test_exc(self): pass
dir: other_dir
file: other_dir/__init__.py
file: other_dir/p.py
import unittest
class T(unittest.TestCase):
  def test_inc(self): pass
dir: inc_dir
file: inc_dir/__init__.py
file: inc_dir/p.py
import unittest
class T(unittest.TestCase):
  def test_inc(self): pass
dir: exc_dir
file: exc_dir/__init__.py
file: exc_dir/p.py
import unittest
class T(unittest.TestCase):
  def test_exc(self): pass
''')

    def assertIDs(self, expected, file_matching=None, dir_matching=None):
        # Matchers collect all by default so test can precisely control what
        # they get. This differs from the Loader class default which provides a
        # better user experience.
        if file_matching is None:
            file_matching = dict(includes=['.*\.py$'])
        if dir_matching is None:
            dir_matching = dict(includes=['.*'])
        loader = self.loader.SubLoader(
            dir_matcher=matchers.NameMatcher(**dir_matching),
            file_matcher=matchers.NameMatcher(**file_matching))
        actual = loader.loadTestsFromFiles('.', os.listdir('.'))
        assertTestIDs(self, expected, actual)

    def test_not_maching_file(self):
        self.assertIDs([], dict(includes=['doesnt_exist']))

    def test_included_file(self):
        self.assertIDs(['inc.T.test_inc'],
                       file_matching=dict(includes=['inc.py']))

    def test_excluded_file(self):
        self.assertIDs(['exc_dir.p.T.test_exc',
                        'inc.T.test_inc', 'inc_dir.p.T.test_inc',
                        'other.T.test_inc', 'other_dir.p.T.test_inc'],
                       # Since matching fails if no rules are given, excluding
                       # one file requires including all files first.
                       file_matching=dict(excludes=['exc.py'],
                                          includes=['.*\.py$']))

    def test_not_matching_dir(self):
        # We get only the tests in the files at the top level
        self.assertIDs(['exc.T.test_exc', 'inc.T.test_inc',
                        'other.T.test_inc'],
                       dir_matching=dict(includes=['doesntexist']))

    def test_included_dir(self):
        self.assertIDs(['exc.T.test_exc',
                        'inc.T.test_inc', 'inc_dir.p.T.test_inc',
                        'other.T.test_inc'],
                       dir_matching=dict(includes=['inc_dir']))

    def test_excluded_dir(self):
        self.assertIDs(['exc.T.test_exc',
                        'inc.T.test_inc', 'inc_dir.p.T.test_inc',
                        'other.T.test_inc', 'other_dir.p.T.test_inc'],
                       # Since matching fails if no rules are given, excluding
                       # one dir requires including all dirs first.
                       dir_matching=dict(excludes=['exc_dir'],
                                         includes=['.*']))

    def test_all(self):
        # No matching specified, we get all tests
        self.assertIDs(['exc.T.test_exc', 'exc_dir.p.T.test_exc',
                        'inc.T.test_inc', 'inc_dir.p.T.test_inc',
                        'other.T.test_inc', 'other_dir.p.T.test_inc'])


class TestLoadTestsFromPackage(unittest.TestCase):

    def setUp(self):
        super(TestLoadTestsFromPackage, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()

    def test_no_package(self):
        self.assertEqual(None, self.loader.loadTestsFromPackage('.'))

    def test_no_init_file(self):
        fixtures.build_tree('''
dir: t
''')
        self.assertEqual(None, self.loader.loadTestsFromPackage('t'))

    def test_import_failure(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
import not_a_python_package
''')
        with self.assertRaises(ImportError):
            self.loader.loadTestsFromPackage('t')

    def test_syntax_error(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
Do I look like python code ?
''')
        with self.assertRaises(SyntaxError):
            self.loader.loadTestsFromPackage('t')

    def test_empty_package(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py''')
        assertTestIDs(self, [], self.loader.loadTestsFromPackage('t'))

    def test_init_tests(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
import unittest
class T(unittest.TestCase):
  def test_init(self): pass
''')
        assertTestIDs(self, ['t.T.test_init'],
                      self.loader.loadTestsFromPackage('t'))

    def test_file_tests(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
file: t/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        assertTestIDs(self, ['t.test.T.test_pass'],
                      self.loader.loadTestsFromPackage('t'))

    def test_only_init_tests(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
def load_tests(loader, std_tests, pattern):
    # We only return the tests defined in __init__.py ignoring anything else
    return std_tests
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
file: t/ignored.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        # Since load_tests is reponsible for all the tests in the tree, the
        # other files are ignored.
        assertTestIDs(self, ['t.T.test_t'],
                      self.loader.loadTestsFromPackage('t'))

    def test_init_and_file_tests(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
file: t/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        assertTestIDs(self, ['t.T.test_t', 't.test.T.test_pass'],
                      self.loader.loadTestsFromPackage('t'))

    def test_none_from_load_tests(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
def load_tests(loader, std_tests, pattern):
    return None
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
file: t/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        # Returning None is obeyed. No other loading is attempted
        self.assertEqual(None, self.loader.loadTestsFromPackage('t'))

    def test_load_tests_overrides(self):
        fixtures.build_tree('''
dir: t
file: t/__init__.py
def load_tests(loader, std_tests, pattern):
    return loader.loadTestsFromFiles('t', ['test.py'])
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
file: t/ignored.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
file: t/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        assertTestIDs(self, ['t.test.T.test_pass'],
                      self.loader.loadTestsFromPackage('t'))


class TestLoadTestsFromTree(unittest.TestCase):

    def setUp(self):
        super(TestLoadTestsFromTree, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()
        # A common base for tests to build upon
        fixtures.build_tree('''
dir: t
file: t/__init__.py
file: t/ignored.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
file: t/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')

    def test_empty(self):
        fixtures.build_tree('''dir: empty''')
        assertTestIDs(self, [], self.loader.loadTestsFromTree('empty'))

    def test_none_from_load_tests(self):
        fixtures.build_tree('''
file: t/__init__.py
def load_tests(loader, std_tests, pattern):
    return None
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
''')
        # Returning None is the same as having an empty module: the loading
        # falls back to iterating the other files.
        assertTestIDs(self, ['t.test.T.test_pass'],
                      self.loader.loadTestsFromTree('.'))

    def test_load_tests_explicit_file(self):
        fixtures.build_tree('''
file: t/__init__.py
def load_tests(loader, std_tests, pattern):
    return loader.loadTestsFromFiles('t', ['test.py'])
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
''')
        assertTestIDs(self, ['t.test.T.test_pass'],
                      self.loader.loadTestsFromTree('.'))

    def test_load_tests_explicit_dir(self):
        fixtures.build_tree('''
file: t/__init__.py
def load_tests(loader, std_tests, pattern):
    return loader.loadTestsFromFiles('t/sub', ['test.py'])
dir: t/sub
file: t/sub/__init__.py
import unittest
class T(unittest.TestCase):
  def test_t(self): pass
file: t/sub/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        # We get the test in 't.sub.test' and ignore the others
        assertTestIDs(self, ['t.sub.test.T.test_pass'],
                      self.loader.loadTestsFromTree('.'))


class TestSubLoader(unittest.TestCase):

    def setUp(self):
        super(TestSubLoader, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.loader = loaders.Loader()
        # A common base for tests to build upon
        fixtures.build_tree('''
dir: t
file: t/__init__.py
file: t/ignored.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
file: t/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')

    def test_load_tests_new_matching_files(self):
        fixtures.build_tree('''
file: t/__init__.py
import os
from olstests import loaders, matchers
def load_tests(loader, std_tests, pattern):
    subloader = loader.SubLoader(
        file_matcher=matchers.NameMatcher(includes=[r'^t\.py$']))
    return subloader.loadTestsFromFiles('t', os.listdir('t'))
file: t/t.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        # We get the test in 't/t.py' and ignore the others
        assertTestIDs(self, ['t.t.T.test_pass'],
                      self.loader.loadTestsFromTree('.'))

    def test_load_tests_new_matching_dirs(self):
        fixtures.build_tree('''
file: t/__init__.py
import os
from olstests import loaders, matchers
def load_tests(loader, std_tests, pattern):
    subloader = loader.SubLoader(
        dir_matcher=matchers.NameMatcher(includes=[r'^t1$']))
    return subloader.loadTestsFromFiles('t', os.listdir('t'))
dir: t/t1
file: t/t1/__init__.py
file: t/t1/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
dir: t/t2
file: t/t2/__init__.py
file: t/t2/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        # We get the test in 't/test.py' because it's loaded before the dir
        # matching applies, 't/t1/test.py' and ignore the others
        assertTestIDs(self, ['t.t1.test.T.test_pass', 't.test.T.test_pass'],
                      self.loader.loadTestsFromTree('.'))

    def test_load_single_test_dir_in_a_root(self):
        fixtures.build_tree('''
dir: t/t1
file: t/t1/__init__.py
file: t/t1/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
dir: t/t2
file: t/t2/__init__.py
file: t/t2/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        root = os.path.join(os.getcwd(), 't')
        sys.path.insert(0, root)
        subloader = self.loader.SubLoader(root=root)
        assertTestIDs(self, ['t1.test.T.test_pass'],
                      subloader.loadTestsFromPackage('t1'))

    def test_load_from_sys_path_module(self):
        fixtures.build_tree('''
dir: t/t1
file: t/t1/__init__.py
file: t/t1/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
dir: t/t2
file: t/t2/__init__.py
file: t/t2/test.py
import unittest
class T(unittest.TestCase):
  def test_pass(self): pass
''')
        sys.path.pop(0)  # Remove the current directory
        sys.path.insert(0, os.path.join(os.getcwd(), 't'))
        assertTestIDs(self, ['t1.test.T.test_pass'],
                      self.loader.loadTestsFromSysPathModule('t1'))
        assertTestIDs(self, ['t2.test.T.test_pass'],
                      self.loader.loadTestsFromSysPathModule('t2'))
