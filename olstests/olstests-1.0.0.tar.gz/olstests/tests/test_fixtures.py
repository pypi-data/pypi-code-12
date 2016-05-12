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
    fixtures,
)


class TestPatch(unittest.TestCase):

    def test_new_attribute(self):
        fixtures.patch(self, self, 'attr', 'hello')
        self.assertEqual('hello', self.attr)

    def test_new_value(self):
        self.attr = 'foo'
        fixtures.patch(self, self, 'attr', 'bar')
        self.assertEqual('bar', self.attr)

    def test_preserved_value(self):
        self.attr = 'foo'

        class LocalTest(unittest.TestCase):

            # We use inner below so 'self' can still refer to the outer test
            def test_it(inner):
                fixtures.patch(inner, self, 'attr', 'bar')
                # inner sees the modified value
                inner.assertEqual('bar', self.attr)

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        # The value has been restored
        self.assertEqual('foo', self.attr)

    def test_removed_attribute_is_restored(self):
        self.attr = 'foo'

        class LocalTest(unittest.TestCase):

            # We use inner below so 'self' can still refer to the outer test
            def test_it(inner):
                fixtures.patch(inner, self, 'attr', 'bar')
                delattr(self, 'attr')
                inner.assertEqual('not there',
                                  getattr(self, 'attr', 'not there'))

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        # The attribute is back with the proper value
        self.assertEqual('foo', self.attr)


class TestCwdToTmp(unittest.TestCase):

    def test_dir_created_and_changed(self):
        cur = os.getcwd()
        fixtures.set_uniq_cwd(self)
        self.assertNotEqual(cur, os.getcwd())

    def test_dir_restored(self):
        self.before = os.getcwd()
        self.during = None

        # To check the cleanup we need to run an inner test
        class LocalTest(unittest.TestCase):

            # We use inner below so 'self' can still refer to the outer test
            def test_it(inner):
                # The current directory has not changed
                inner.assertEqual(self.before, os.getcwd())
                fixtures.set_uniq_cwd(inner)
                # The current directory has changed
                inner.assertNotEqual(self.before, os.getcwd())
                self.during = os.getcwd()

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        # The current directory has been restored
        self.assertEqual(self.before, os.getcwd())

    def test_dir_default_prefix(self):
        fixtures.set_uniq_cwd(self)
        cur = os.getcwd()
        # Default is to name the tmp dir after the test method
        prefix = self._testMethodName
        self.assertTrue(os.path.basename(cur).startswith(prefix))

    def test_dir_prefix_provided(self):
        fixtures.set_uniq_cwd(self, 'provided')
        cur = os.getcwd()
        self.assertTrue(os.path.basename(cur).startswith('provided'))


class TestProtectImports(unittest.TestCase):

    def setUp(self):
        super(TestProtectImports, self).setUp()
        fixtures.protect_imports(self)

    def test_added_module_is_removed(self):
        self.assertIs(None, sys.modules.get('foo', None))

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                sys.modules['foo'] = 'bar'

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertIs(None, sys.modules.get('foo', None))

    def test_removed_module_is_restored(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                del sys.modules['I_dont_exist']

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_modified_module_is_restored(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                sys.modules['I_dont_exist'] = 'qux'

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_modified_sys_path_is_restored(self):
        fixtures.set_uniq_cwd(self)
        inserted = self.uniq_dir
        self.assertFalse(inserted in sys.path)

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                sys.path.insert(0, inserted)

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertFalse(inserted in sys.path)


class TestEnv(unittest.TestCase):

    def test_env_preserved(self):
        os.environ['NOBODY_USES_THIS'] = 'foo'

        class Inner(unittest.TestCase):

            def test_overridden(self):
                fixtures.isolate_from_env(self, {'NOBODY_USES_THIS': 'bar'})
                self.assertEqual('bar', os.environ['NOBODY_USES_THIS'])

        assertions.assertSuccessfullTest(self, Inner('test_overridden'))
        self.assertEqual('foo', os.environ['NOBODY_USES_THIS'])

    def test_env_var_deleted(self):
        os.environ['NOBODY_USES_THIS'] = 'foo'

        class Inner(unittest.TestCase):

            def test_deleted(self):
                fixtures.isolate_from_env(self, {'NOBODY_USES_THIS': None})
                self.assertIs('deleted',
                              os.environ.get('NOBODY_USES_THIS', 'deleted'))
        assertions.assertSuccessfullTest(self, Inner('test_deleted'))
        self.assertEqual('foo', os.environ['NOBODY_USES_THIS'])


class TestBuildTreeFromDesc(unittest.TestCase):

    def setUp(self):
        super(TestBuildTreeFromDesc, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_empty_description(self):
        self.assertEqual([], os.listdir('.'))
        fixtures.build_tree('')
        self.assertEqual([], os.listdir('.'))

    def test_single_line_without_return(self):
        self.assertEqual([], os.listdir('.'))
        fixtures.build_tree('file: foo')
        self.assertEqual(['foo'], os.listdir('.'))
        with open('foo') as f:
            self.assertEqual('', f.read())

    def test_leading_line_is_ignored(self):
        self.assertEqual([], os.listdir('.'))
        fixtures.build_tree('tagada\nfile: foo')
        self.assertEqual(['foo'], os.listdir('.'))
        with open('foo') as f:
            self.assertEqual('', f.read())

    def test_orphan_line_is_ignored(self):
        self.assertEqual([], os.listdir('.'))
        fixtures.build_tree('''
dir: foo
orphan line
file: foo/bar.py
baz
''')
        self.assertEqual(['foo'], os.listdir('.'))
        self.assertEqual(['bar.py'], os.listdir('foo'))
        with open('foo/bar.py') as f:
            self.assertEqual('baz\n', f.read())

    def test_empty_file_content(self):
        fixtures.build_tree('''file: foo''')
        with open('foo') as f:
            self.assertEqual('', f.read())

    def test_simple_file_content(self):
        fixtures.build_tree('''file: foo
tagada
''')
        with open('foo') as f:
            self.assertEqual('tagada\n', f.read())

    def test_file_content_in_a_dir(self):
        fixtures.build_tree('''dir: dir
file: dir/foo
bar
''')
        with open('dir/foo') as f:
            self.assertEqual('bar\n', f.read())

    def test_simple_symlink_creation(self):
        fixtures.build_tree('''file: foo
tagada
link: foo bar
''')
        with open('foo') as f:
            self.assertEqual('tagada\n', f.read())
        with open('bar') as f:  # Yeah ! Open Bar !
            self.assertEqual('tagada\n', f.read())

    def test_broken_symlink_creation(self):
        fixtures.build_tree('''link: foo bar
''')
        self.assertEqual('foo', os.readlink('bar'))

    def test_invalid_symlink_description_raises(self):
        with self.assertRaises(ValueError) as cm:
            fixtures.build_tree('''link: foo
''')
        self.assertEqual('Invalid link description: foo', cm.exception.args[0])
