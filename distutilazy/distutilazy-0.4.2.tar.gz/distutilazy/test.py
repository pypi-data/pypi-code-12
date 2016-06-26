"""
distutilazy.test
-----------------

command classes to help run tests

:license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

import os
from os.path import abspath, basename, dirname
import sys
import fnmatch
from importlib import import_module
import unittest
from distutils.core import Command
from types import ModuleType

__version__ = "0.4.0"


def test_suite_for_modules(modules):
    suite = unittest.TestSuite()
    test_loader = unittest.defaultTestLoader
    for module in modules:
        module_tests = test_loader.loadTestsFromModule(module)
        suite.addTests(module_tests)
    return suite


def find_source_filename(source_name, dir_path):
    """Find the filename matching the source/module name
    in the specified path. For example searching for "queue"
    might return "queue.py" or "queue.pyc"
    """
    source_filenames = [
            os.path.join(dir_path, source_name + ext) for
            ext in (".py", "pyc")]
    for source_filename in source_filenames:
        if os.path.exists(source_filename):
            return source_filename
    return None


class RunTests(Command):
    description = """Run test suite"""
    user_options = [("root=", "r", "path to tests suite dir"),
                    ("pattern=", "p", "test file name pattern"),
                    ("verbosity=", "v", "verbosity level [1,2,3]"),
                    ("files=", None,
                     "run specified test files (comma separated)"),
                    ("except-import-errors", None,
                        "except import errors when trying to import test " \
                        "modules. Note: might shadow import errors raised " \
                        "by the actual modules being tested")]

    def initialize_options(self):
        self.root = os.path.join(os.getcwd(), 'tests')
        self.pattern = "test*.py"
        self.verbosity = 1
        self.files = None
        self.except_import_errors = False

    def finalize_options(self):
        if not os.path.exists(self.root):
            raise IOError("Failed to access root path '{}'".format(self.root))
        verbosity = min(int(self.verbosity), 3)
        if verbosity < 1:
            self.verbosity = 1
        else:
            self.verbosity = verbosity
        if self.files:
            self.files = map(lambda name: name.strip(), self.files.split(','))
        self.except_import_errors = bool(self.except_import_errors)

    def get_modules_from_files(self, files):
        modules = []
        for file_name in files:
            directory = dirname(file_name)
            module_name, _, extension = basename(file_name).rpartition('.')
            if not module_name:
                self.announce(
                    "failed to find module name from filename '{}'." +
                    "skipping this file".format(file_name))
                continue
            package_name = self._import_dir_as_package(directory)
            if package_name:
                module_name = '.' + module_name
            elif directory not in sys.path:
                sys.path.insert(0, directory)
            self.announce(
                "importing module '{}' from file '{}' ...".format(module_name,
                                                                  file_name))
            module = import_module(module_name, package=package_name)
            modules.append(module)
        return modules

    def _import_dir_as_package(self, directory):
        """Tries to import the specified directory path as a package, if it
        seems to be a package. Returns the package name (if import was
        successful) or None if directory is not a valid package."""

        directory_name = basename(directory)
        abs_dir = abspath(directory)
        package_name = None
        if directory_name and find_source_filename('__init__', abs_dir) is not None:
            parent_dir = dirname(abs_dir)
            if not parent_dir in sys.path:
                sys.path.insert(0, parent_dir)
            try:
                self.announce(
                    "importing '{}' as package ...".format(directory_name))
                import_module(directory_name)
                package_name = directory_name
            except ImportError as err:
                self.announce(
                    "failed to import '{}'. {}".format(directory_name, err))
                if self.except_import_errors and directory_name in str(err):
                    package_name = None
                else:
                    raise err
        return package_name

    def find_test_modules_from_package_path(self, package_path):
        """Import and return modules from package __all__,
        if path is found to be a package.
        """
        package_dir = dirname(package_path)
        package_name = basename(package_path)
        if package_dir:
            sys.path.insert(0, package_dir)
        self.announce(
            "importing package '{}' ...".format(package_name)
        )
        package = import_module(package_name)
        if package and hasattr(package, '__all__'):
            modules = []
            for module_name in package.__all__:
                module = import_module('{}.{}'.format(
                    package_name, module_name))
                if type(module) == ModuleType \
                        and module not in modules:
                    modules.append(module)
            return modules

    def find_test_modules_from_test_files(self, root, pattern):
        """Return list of test modules from the the files in the path
        whose name match the pattern
        """
        modules = []
        abs_root = abspath(root)
        for (dir_path, directories, file_names) in os.walk(abs_root):
            package_name = self._import_dir_as_package(dir_path)
            if not package_name and not dir_path in sys.path:
                sys.path.insert(0, dir_path)
            for filename in fnmatch.filter(file_names, pattern):
                module_name, _, extension = basename(filename).rpartition('.')
                if not module_name:
                    self.announce(
                        "failed to find module name from filename '{}'." +
                        "skipping this test".format(filename))
                    continue
                module_name_to_import = '.' + module_name if package_name else module_name
                self.announce(
                    "importing module '{}' from '{}' ...".format(
                        module_name_to_import, filename
                    )
                )
                try:
                    module = import_module(module_name_to_import, package_name)
                    if type(module) == ModuleType and module not in modules:
                        modules.append(module)
                except ImportError as err:
                    self.announce(
                        "failed to import '{}' from '{}'. {}." +
                        "skipping this file!".format(module_name_to_import, filename, err)
                    )
                    if not self.except_import_errors or module_name not in str(err):
                        raise err
                except (ValueError, SystemError) as err:
                    self.announce(
                        "failed to import '{}' from '{}'. {}." +
                        "skipping this file!".format(module_name, filename, err)
                    )
        return modules

    def get_test_runner(self):
        return unittest.TextTestRunner(verbosity=self.verbosity)

    def run(self):
        if self.files:
            modules = self.get_modules_from_files(self.files)
        else:
            self.announce("searching for test package modules ...")
            modules = self.find_test_modules_from_package_path(self.root)
            if not modules:
                self.announce("searching for test files ...")
                modules = self.find_test_modules_from_test_files(self.root,
                                                                 self.pattern)
        if not modules:
            self.announce("found no test files")
            return False
        suite = test_suite_for_modules(modules)
        runner = self.get_test_runner()
        self.announce("running tests ...")
        runner.run(suite)

run_tests = RunTests
