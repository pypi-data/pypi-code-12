"""
distutilazy.tests.test_test
----------------------------

Tests for distutilazy.test module

:license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

import sys
from os.path import dirname, basename, abspath
from os.path import join as path_join
from distutils.dist import Distribution
from unittest import TestCase, TestSuite, main

TESTS_PATH = dirname(__file__)
sys.path.insert(0, dirname(TESTS_PATH))
sys.path.insert(0, TESTS_PATH)

from distutilazy.test import RunTests, test_suite_for_modules

FIXTURES = path_join(dirname(abspath(__file__)), 'fixtures', 'test_test')
current_test_file = basename(__file__[:-1] if __file__.endswith('.pyc') else __file__)


def get_module_names(modules):
    return map(lambda m: m.__name__, modules)


class TestTest(TestCase):

    def test_find_modules_from_package_path(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        modules = test_runner.find_test_modules_from_package_path(TESTS_PATH)
        self.assertIn('tests.test_test', get_module_names(modules))

    def test_get_modules_from_files(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        self.assertEqual(
            [], test_runner.get_modules_from_files(['none_existing_file']))
        modules = test_runner.get_modules_from_files([current_test_file])
        self.assertEqual(1, len(modules))
        self.assertEqual('test_test', modules.pop().__name__)

    def test_find_test_modules_from_test_files(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        modules = test_runner.find_test_modules_from_test_files(
            TESTS_PATH, 'none_exiting_pattern')
        self.assertEqual([], modules)
        modules = test_runner.find_test_modules_from_test_files(TESTS_PATH, current_test_file)
        self.assertEqual(1, len(modules))
        self.assertEqual('tests.test_test', modules.pop().__name__)
        modules = test_runner.find_test_modules_from_test_files(TESTS_PATH, 'test_*')
        module_names = get_module_names(modules)
        self.assertIn('tests.test_test', module_names)
        self.assertIn('subpackage.test_subpackage', module_names)

    def test_find_test_modules_from_test_files_raises_import_errors(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        self.assertRaises(
            ImportError,
            test_runner.find_test_modules_from_test_files,
            FIXTURES,
            'hasimport*'
        )

    def test_find_test_modules_from_test_files_wont_shadow_import_errors(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        test_runner.except_import_errors = True
        self.assertRaises(
            ImportError,
            test_runner.find_test_modules_from_test_files,
            FIXTURES,
            'hasimport*'
        )

    def test_find_test_modules_from_test_files_imports_from_subdirectories(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        directory_path = path_join(FIXTURES, "subdir")
        modules = test_runner.find_test_modules_from_test_files(
            directory_path, 'samplemodule*')
        self.assertEquals(
            ['samplemodule'],
            get_module_names(modules)
        )

    def test_test_suite_for_modules(self):
        self.assertIsInstance(test_suite_for_modules([]), TestSuite)

    def test_get_test_runner(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        runner = test_runner.get_test_runner()
        self.assertTrue(hasattr(runner, 'run'))
        self.assertTrue(hasattr(runner.run, '__call__'))

    def test_get_modules_from_files_raises_import_error_if_any(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        filename = path_join(FIXTURES, "hasimporterr.py")
        self.assertRaises(ImportError, test_runner.get_modules_from_files, [filename])

    def test_get_modules_from_files_does_no_shadow_import_errors_when_excepting_errors(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        test_runner.except_import_errors = True
        filename = path_join(FIXTURES, "hasimporterr.py")
        self.assertRaises(ImportError, test_runner.get_modules_from_files, [filename])

    def test_find_test_modules_from_test_files_raises_import_error(self):
        dist = Distribution()
        test_runner = RunTests(dist)
        test_runner.finalize_options()
        self.assertRaises(ImportError,
                          test_runner.find_test_modules_from_test_files,
                          TESTS_PATH, 'hasimporterr*')


if __name__ == '__main__':
    main()
