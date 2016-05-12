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
"""A collection of commonly used 'Features' to optionally run tests."""

from distutils import spawn
import platform
import unittest


class Feature(object):
    """An operating system Feature."""

    def __init__(self):
        self._available = None

    def available(self):
        """Is the feature available?

        :return: True if the feature is available.
        """
        if self._available is None:
            self._available = self._probe()
        return self._available

    def _probe(self):
        """Implement this method in concrete features.

        :return: True if the feature is available.
        """
        raise NotImplementedError

    def feature_name(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.feature_name()

    def __unicode__(self):
        return self.feature_name()


class ExecutableFeature(Feature):
    """Feature testing whether an executable of a given name is on the PATH."""

    def __init__(self, name):
        super(ExecutableFeature, self).__init__()
        self.name = name
        self._path = None

    @property
    def path(self):
        # This is a property, so accessing path ensures _probe was called
        self.available()
        return self._path

    def _probe(self):
        self._path = spawn.find_executable(self.name)
        return self._path is not None

    def feature_name(self):
        return '{} executable'.format(self.name)


class PlatformFeature(Feature):
    """Feature testing the current platform."""

    def __init__(self):
        super(PlatformFeature, self).__init__()
        # self.distro structure may vary between distros, the daughter classes
        # handle the differences.
        self.distro = platform.linux_distribution()


class UbuntuPlatformFeature(PlatformFeature):
    """Feature testing the current ubuntu release where the tests are run."""

    def __init__(self, expected_id):
        super(UbuntuPlatformFeature, self).__init__()
        self.expected_id = expected_id
        self._name, self._version, self.actual_id = self.distro

    def feature_name(self):
        return self.expected_id

    def _probe(self):
        return (self._name == 'Ubuntu' and self.expected_id == self.actual_id)

    @property
    def version(self):
        """The Ubuntu version (yy.mm) string.

        This property is available even when we run on a different version,
        so we *don't* call _probe().
        """
        return self._version


trusty = UbuntuPlatformFeature('trusty')
utopic = UbuntuPlatformFeature('utopic')
vivid = UbuntuPlatformFeature('vivid')
wily = UbuntuPlatformFeature('wily')
xenial = UbuntuPlatformFeature('xenial')


def requires(feature):
    """A decorator to skip a test if a feature is not available.

    If the feature is not available, a test case or a test suite using this
    decorator will be skipped.
    """
    if not feature.available():
        reason = '{} is not available'.format(feature.feature_name())
        return unittest.skip(reason)

    # If the feature is available, there is no need to decorate
    return lambda obj: obj
