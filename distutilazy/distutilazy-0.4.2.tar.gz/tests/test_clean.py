"""
distutilazy.tests.test_clean
----------------------------

Tests for distutilazy.clean module
"""

from __future__ import absolute_import

import sys
from shutil import rmtree
from os import path, mkdir
from os.path import dirname, abspath
from unittest import TestCase, main
from distutils.dist import Distribution
from tempfile import mkstemp, mkdtemp

here = dirname(__file__)
sys.path.insert(0, dirname(here))
sys.path.insert(0, here)

from distutilazy.clean import CleanPyc, CleanAll, CleanJythonClass


class TestCleanPyc(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_cache_dir = abspath(path.join(here, '_test_py_cache_'))
        if path.exists(cls.test_cache_dir):
            raise Exception(
                    "Test python cache directory exists in '{}'." \
                    " Please remove this path".format(cls.test_cache_dir)
                    )
        mkdir(cls.test_cache_dir)

    @classmethod
    def tearDownAfter(cls):
        if path.exists(cls.test_cache_dir):
            rmtree(cls.test_cache_dir, True)

    def test_clean_pyc(self):
        try:
            temp_files = []
            temp_dir = mkdtemp(suffix='_distutilazy_test')
            for i in range(5):
                _, temp_filename = mkstemp(suffix=".pyc", dir=temp_dir)
                temp_files.append(temp_filename)
            temp_files.sort()
            dist = Distribution()
            pyc_cleaner = CleanPyc(dist)
            pyc_cleaner.root = temp_dir
            pyc_cleaner.finalize_options()
            self.assertEqual(
                    sorted(pyc_cleaner.find_compiled_files()),
                    temp_files
            )
            pyc_cleaner.run()

            for temp_filename in temp_files:
                self.assertFalse(path.exists(temp_filename))
        finally:
            if path.exists(temp_dir):
                rmtree(temp_dir, True)

    def test_clean_pyc_finds_nothing(self):
        dist = Distribution()
        pyc_cleaner = CleanPyc(dist)
        pyc_cleaner.extensions = ".ppyycc, .ppyyoo"
        pyc_cleaner.finalize_options()
        self.assertEqual(pyc_cleaner.extensions, [".ppyycc", ".ppyyoo"])
        self.assertEqual(pyc_cleaner.find_compiled_files(), [])

    def test_clean_py_cache_dirs(self):
        dist = Distribution()
        pycache_cleaner = CleanPyc(dist)
        pycache_cleaner.directories = "_test_py_cache_"
        pycache_cleaner.finalize_options()
        self.assertEqual(pycache_cleaner.directories, ["_test_py_cache_"])
        self.assertEqual(
            pycache_cleaner.find_cache_directories(),
            [self.__class__.test_cache_dir]
        )
        pycache_cleaner.run()
        self.assertFalse(path.exists(self.__class__.test_cache_dir))

    def test_clean_py_cache_dirs_finds_nothing(self):
        dist = Distribution()
        pycache_cleaner = CleanPyc(dist)
        pycache_cleaner.extensions = ".ppyycc, .ppyyoo"
        pycache_cleaner.directories = "not_exist, and_not_found"
        pycache_cleaner.finalize_options()
        self.assertEqual(
            pycache_cleaner.directories,
            ["not_exist", "and_not_found"]
        )
        self.assertEqual(pycache_cleaner.find_cache_directories(), [])


class TestCleanAll(TestCase):

    def test_clean_all(self):
        dist = Distribution()
        dist.metadata.name = "test_dist"
        all_cleaner = CleanAll(dist)
        all_cleaner.finalize_options()
        self.assertEqual(all_cleaner.get_egginfo_dir(), "test_dist.egg-info")
        targets = ["build", "dist", "egginfo", "extra"]
        bad_calls = []
        good_calls = []
        good_calls_should_be = 0
        for target in targets:
            all_cleaner = CleanAll(dist)
            all_cleaner.finalize_options()
            all_cleaner.dry_run = True
            setattr(all_cleaner, "keep_%s" % target, True)
            setattr(all_cleaner, "clean_%s" % target,
                    lambda x: bad_calls.append(target))
            other_targets = [t for t in targets if t != target]
            for other_target in other_targets:
                good_calls_should_be += 1
                setattr(all_cleaner, "clean_%s" % other_target,
                        lambda x=None: good_calls.append(other_target))
            all_cleaner.run()
        self.assertEqual(bad_calls, [])
        self.assertEqual(len(good_calls), good_calls_should_be)


class TestCleanJythonClass(TestCase):

    def test_clean_classes_finds_nothing(self):
        dist = Distribution()
        pyc_cleaner = CleanJythonClass(dist)
        pyc_cleaner.extensions = "$py.cla$$, .clazz"
        pyc_cleaner.finalize_options()
        self.assertEqual(pyc_cleaner.extensions, ["$py.cla$$", ".clazz"])
        self.assertEqual(pyc_cleaner.find_class_files(), [])

    def test_clean_class(self):
        try:
            temp_files = []
            temp_dir = mkdtemp(suffix='_distutilazy_test')
            for i in range(5):
                _, temp_filename = mkstemp(suffix="$py.class", dir=temp_dir)
                temp_files.append(temp_filename)
            temp_files.sort()
            dist = Distribution()
            jython_cleaner = CleanJythonClass(dist)
            jython_cleaner.root = temp_dir
            jython_cleaner.finalize_options()
            self.assertEqual(
                    sorted(jython_cleaner.find_class_files()),
                    temp_files
            )
            jython_cleaner.run()

            for temp_filename in temp_files:
                self.assertFalse(path.exists(temp_filename))
        finally:
            if path.exists(temp_dir):
                rmtree(temp_dir, True)


if __name__ == "__main__":
    main()
