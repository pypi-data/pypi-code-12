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

from distutils import spawn

from olstests import (
    assertions,
    features,
    fixtures,
)


if sys.version_info >= (3,):
    unicode = str


class TestFeature(unittest.TestCase):

    def test_caching(self):

        class InstrumentedFeature(features.Feature):
            def __init__(self):
                super(InstrumentedFeature, self).__init__()
                self.calls = []

            def _probe(self):
                self.calls.append('_probe')
                return False

        feature = InstrumentedFeature()
        feature.available()
        self.assertEqual(['_probe'], feature.calls)
        # Feature._probe is called by the feature at most once.
        feature.available()
        self.assertEqual(['_probe'], feature.calls)

    def test_named(self):
        """Feature.__unicode__ should thunk to feature_name()."""
        class NamedFeature(features.Feature):
            def feature_name(self):
                return 'datsmyname'
        feature = NamedFeature()
        self.assertEqual('datsmyname', unicode(feature))

    def test_default(self):
        """Feature.__unicode__ should default to __class__.__name__."""
        class NamedFeature(features.Feature):
            pass
        feature = NamedFeature()
        self.assertEqual('NamedFeature', unicode(feature))


class TestUbuntuPlatformFeature(unittest.TestCase):

    def test_trusty(self):
        trusty = features.UbuntuPlatformFeature('trusty')
        # Inject known values
        trusty._name = 'Ubuntu'
        trusty._version = '14.04'
        trusty.actual_id = 'trusty'
        self.assertTrue(trusty.available())


def set_uniq_path(test):
    fixtures.set_uniq_cwd(test)
    test.bin1_dir = os.path.join(test.uniq_dir, 'bin1')
    test.bin2_dir = os.path.join(test.uniq_dir, 'bin2')
    os.mkdir(test.bin1_dir)
    os.mkdir(test.bin2_dir)
    fixtures.isolate_from_env(
        test,
        {'PATH': os.pathsep.join([test.bin1_dir, test.bin2_dir])})


def make_file(path, content, chmod_bits=0o644):
    with open(path, 'w') as f:
        f.write(content)
    os.chmod(path, chmod_bits)


class TestFindExecutable(unittest.TestCase):

    def setUp(self):
        super(TestFindExecutable, self).setUp()
        set_uniq_path(self)

    def test_not_in_path(self):
        self.assertIsNone(spawn.find_executable('I DONT EXIST'))

    def test_not_executable_is_selected_too_bad(self):
        path1 = os.path.join(self.bin1_dir, 'doit')
        make_file(path1, 'whatever')
        # Despite 'whatever' not having the 'x' chmod bit it ends up being
        # selected.
        self.assertEqual(path1, spawn.find_executable('doit'))

    def test_executable(self):
        doit_path = os.path.join(self.bin1_dir, 'doit')
        make_file(doit_path, 'whatever', 0o755)
        self.assertEqual(doit_path, spawn.find_executable('doit'))

    def test_non_executable_not_ignored(self):
        path1 = os.path.join(self.bin1_dir, 'doit')
        make_file(path1, 'whatever')
        path2 = os.path.join(self.bin2_dir, 'doit')
        make_file(path2, 'whatever', 0o755)
        # Despite 'whatever' not having the 'x' chmod bit it ends up being
        # selected.
        self.assertEqual(path1, spawn.find_executable('doit'))


class TestExecutableFeature(unittest.TestCase):

    def setUp(self):
        super(TestExecutableFeature, self).setUp()
        set_uniq_path(self)

    def test_feature_not_available(self):
        feature = features.ExecutableFeature('DO NOT EXIST')
        self.assertFalse(feature.available())

    def test_feature_available(self):
        feature = features.ExecutableFeature('doit')
        doit_path = os.path.join(self.bin1_dir, 'doit')
        make_file(doit_path, 'whatever', 0o755)
        self.assertTrue(feature.available())


class TestingFeature(features.Feature):
    """A Feature that can be set to be available or not at build time."""

    def __init__(self, available):
        super(TestingFeature, self).__init__()
        # Short-circuit the probe by directly modifying the caching attribute
        self._available = available


class TestRequires(unittest.TestCase):

    def test_skip_not_available(self):
        feature = TestingFeature(False)

        class LocalTest(unittest.TestCase):

            @features.requires(feature)
            def test_it(inner):
                raise self.failureException('This should have been skipped')

        res = assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        assertions.assertLength(self, 1, res.skipped)

    def test_pass_available(self):
        feature = TestingFeature(True)

        class LocalTest(unittest.TestCase):

            @features.requires(feature)
            def test_it(inner):
                pass

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))

    def test_errors_when_used_without_a_feature(self):
        feature = object()

        with self.assertRaises(AttributeError) as cm:

            class LocalTest(unittest.TestCase):

                @features.requires(feature)
                def test_it(inner):
                    msg = 'An error should have been encountered earlier'
                    raise self.failureException(msg)

        msg = "'object' object has no attribute 'available'"
        self.assertEqual(msg, str(cm.exception))
