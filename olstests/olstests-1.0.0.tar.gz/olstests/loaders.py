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
"""Load tests from a file system tree.

Python tests themselves are generally organized as a subtree of a python
module.

There is a one to one relationship between a source file and a python module
as well as between a directory and a python package.

In the most common cases, loading all the tests for a given package is just
scanning the file system recursively from the package root, importing every
python file and loading the tests defined there if any. By default,
ols-tests will load all the tests in packages existing in the current
directory.

Alternatively, the package root can be obtained from an importable module.

Yet, some tests are not written in python and have different loading strategies
(including file/directory name matching). Even some python packages or even
just scripts may want to change this policy.

The Loader.SubLoader() method is aimed at making these policy changes as
easy as possible at any point in the python package hierarchy traversal.

Relying on the load_tests protocol, each python package or module can define
how the tests in a given subtree (down to a single module) should be loaded.
So an arbitrary tree containing tests can be populated with __init__.py files
to change the loading policy for specific subtrees. This applies equally weel
to python tests or any arbitrary kind of test (the latter requires subclassing
Loader to load the tests from the files themselves though ;).
"""
import functools
import importlib
import os
import sys
import traceback
import unittest


from olstests import matchers


class Loader(unittest.TestLoader):
    """Load tests from an arbitrary tree.

    This also provides ways for packages to define the test discovery and
    loading as they see fit by subclassing.

    Sorting happens on base names inside a directory while walking the tree
    and on test class names and test method names when loading a
    module. Those sortings combined provide a test suite where test ids are
    sorted alphabetically.

    :note: The default sorting is alphabetical and is the only working
        one. While this loader sort file (and dir) names using
        'unittest.TestLoader.sortTestMethodsUsing', the later, while
        respecting that for test methods, relies on 'dir(module)' providing
        the test *classes* in alphabetical order and doesn't sort them with
        'sortTestMethodsUsing' which after all is what the name implies.
    """
    def __init__(self, *args, **kwargs):
        """Defines a test loader.

        :param files: A NameMatcher object to select the files that may contain
            tests. Default to all python source files starting with 'test'.

        :param dirs: A NameMatcher object to select the directories that may
            contain tests. Default to all directory names.

        :param root: An alternate starting point for the loading. Defaults
            to current directory.
        """
        root = kwargs.pop('root', os.getcwd())
        file_matcher = kwargs.pop(
            'file_matcher', matchers.NameMatcher(includes=[r'^test.*\.py$']))
        # MISSINGTEST: The default dir matcher should be restricted to valid
        # python identifiers. -- vila 2014-01-27
        dir_matcher = kwargs.pop(
            'dir_matcher', matchers.NameMatcher(includes=[r'^[^.]*$']))
        super(Loader, self).__init__(*args, **kwargs)
        self.root = root
        self.file_matcher = file_matcher
        self.dir_matcher = dir_matcher

    def SubLoader(self, *args, **kwargs):
        """Creates a new loader overriding load policy.

        :param root: Optional. A new root to redirect the tree traversal.

        :param file_matcher: Optional. A new matcher to filter files.

        :param dir_matcher: Optional. A new matcher to filter directories.

        :return: A new loader with the new policy, leaving the original loader
            untouched.
        """
        root = kwargs.pop('root', self.root)
        file_matcher = kwargs.pop('file_matcher', self.file_matcher)
        dir_matcher = kwargs.pop('dir_matcher', self.dir_matcher)
        # Create a clone copying the attributes that defines the current policy
        # if no specific values are provided by the caller.
        return self.__class__(*args, root=root,
                              file_matcher=file_matcher,
                              dir_matcher=dir_matcher,
                              **kwargs)

    def abspath(self, *parts):
        """Return an absolute path from a list of relative path parts.

        :param parts: Any number of path parts (including 0).

        The loader API expect relative paths but internally needs absolute
        paths from the loader root (generally the current directory when the
        loading started or the sys.path directory a package was imported from).
        """
        return os.path.join(self.root, *parts)

    def loadTestsFromTree(self, dir_path):
        """Load all tests in a tree and return the resulting suite.

        :param dir_path: The directory where the load starts.

        :return: The test suite of all collected tests in the tree, sorted, as
            defined by 'sortTestMethodsUsing', using the dir name and file
            names as keys.
        """
        suite = self.loadTestsFromPackage(dir_path)
        if suite is not None:
            return suite
        suite = self.suiteClass()
        names = os.listdir(self.abspath(dir_path))
        suite.addTests(self.loadTestsFromFiles(dir_path, names))
        return suite

    def loadTestsFromPackage(self, dir_path):
        """Load the tests defined in a python package.

        :param dir_path: The directory defining the package.

        :return: The test suite of all the tests defined in the package using
             the unittest 'load_test' protocol if appropriate. The tests are
             sorted as defined by 'sortTestMethodsUsing', using the dir name
             and file names as keys.
        """
        init_path = os.path.join(dir_path, '__init__.py')
        if not os.path.isfile(self.abspath(init_path)):
            # No python module here, nothing to load
            return None
        try:
            package = self.importFromPath(dir_path)
        except TypeError:
            # This can occur when 'dir_path' contains chars that are
            # illegal for a module name. In that case, it's not a package
            # or it should be imported from a different path (in sys.path).
            return None

        # Can we delegate to the package ?
        load_tests = getattr(package, 'load_tests', None)
        if load_tests is not None:
            # let unittest handle the 'load_tests' protocol
            return self.loadTestsFromModule(package)
        # Otherwise, If tests are defined in the package, load them

        # FIXME: Allow the suite class to be speficied in the module in a
        # load_tests compatible way (if that makes sense) -- vila 2016-04-23
        suite = self.suiteClass()
        suite.addTests(self.loadTestsFromModule(package))
        # And load the tests from the other files
        file_names = os.listdir(self.abspath(dir_path))
        file_names.remove('__init__.py')
        suite.addTests(self.loadTestsFromFiles(dir_path, file_names))
        return suite

    def loadTestsFromFiles(self, dir_path, file_names):
        """Load all tests in a list of filenames inside a dir.

        :param dir_path: The directory where the load starts.

        :param file_names: A possibly empty list of file and dir names to
            collect tests from.

        :return: The test suite of all collected tests in matched file and dir
            names in the tree rooted at 'dir_path' (the current 'file_matcher'
            and 'dir_matcher' are used against dir/file names). No sorting is
            done here but the filenames order is preserved as well as the order
            of the collected test suites.
        """
        # Walk the tree to discover the tests
        suite = self.suiteClass()
        for file_name in self.sortNames(file_names):
            rel_path = os.path.join(dir_path, file_name)
            if os.path.isfile(self.abspath(rel_path))\
                    and self.file_matcher.matches(file_name):
                suite.addTests(self.loadTestsFromFile(rel_path))
            elif os.path.isdir(self.abspath(rel_path))\
                    and self.dir_matcher.matches(file_name):
                suite.addTests(self.loadTestsFromTree(rel_path))
        return suite

    def loadTestsFromFile(self, path):
        """Load all tests in a given file.

        :param path: The path of the file.

        :return: The test suite of all tests collected in the file after the
            corresponding module is imported, using the test class and test
            method names as keys.
        """
        module = self.importFromPath(path)
        return self.loadTestsFromModule(module)

    def packageSysPathFromName(self, name):
        """Find where a package resides on disk.

        This can fail if the package cannot be imported but is guaranteed to
        succeed otherwise.

        :param name: The python package name as it appears in the import
            statement.

        :return: A (sys_path_entry, rel_path) tuple where sys_path_entry is the
            entry in sys.path from where the package is imported and rel_path
            is the relative path from that sys path entry.
        """
        mod = importlib.import_module(name)
        mod_abs_dir = os.path.abspath(os.path.dirname(mod.__file__))
        mod_rel_path = name.replace('.', os.sep)
        # Find which part of sys.path provided the module
        for p in sys.path:
            abs_path = os.path.abspath(os.path.join(p, mod_rel_path))
            if abs_path == mod_abs_dir:
                sys_path_entry = p
                break
        return sys_path_entry, mod_rel_path

    def loadTestsFromSysPathModule(self, name):
        """Load all tests in an importable module.

        :param name: The [dotted] module name.

        Instead of walking the file system from a given directory, use the
        directory the module is imported from.
        """
        sys_path_entry, mod_rel_path = self.packageSysPathFromName(name)
        subloader = self.SubLoader(root=sys_path_entry)
        return subloader.loadTestsFromPackage(mod_rel_path)

    def sortNames(self, names):
        """Return 'names' sorted as defined by sortTestMethodsUsing.

        It's a little abuse of sort*TestMethods*Using as we're sorting file
        names (or even module python paths) but it allows providing a
        consistent order for the whole suite.
        """
        return sorted(names,
                      key=functools.cmp_to_key(self.sortTestMethodsUsing))

    def importFromPath(self, path):
        imp_path = os.path.normpath(path)
        if imp_path.endswith('.py'):
            imp_path = imp_path[:-3]  # Remove the trailing '.py'
        mod_name = imp_path.replace(os.path.sep, '.')
        try:
            return importlib.import_module(mod_name)
        except ImportError:
            tb = traceback.format_exc()
            msg = 'Failed to import {} at {}:\n{}'.format(mod_name, path, tb)
            raise ImportError(msg)
