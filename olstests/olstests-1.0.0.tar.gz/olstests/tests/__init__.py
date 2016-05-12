# This file is part of the Online Services test tools
#
# Copyright 2013, 2014 Canonical Ltd.
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


from olstests import (
    features,
)


class MinimalTesttools(features.Feature):

    def _probe(self):
        import testtools
        return testtools.__version__ >= (0, 9, 30)


minimal_testtools = MinimalTesttools()


class MinimalPep8(features.Feature):
    # Supporting precise is just too much work, requires at least the saucy
    # version

    def _probe(self):
        import pep8
        return pep8.__version__ >= '1.4.6'


minimal_pep8 = MinimalPep8()


class MinimalPyflakes(features.Feature):
    # Supporting precise is just too much work, requires at least the saucy
    # version

    def _probe(self):
        import pyflakes
        return pyflakes.__version__ >= '0.7.3'


minimal_pyflakes = MinimalPyflakes()


class AtLeastUbuntu(features.UbuntuPlatformFeature):

    def _probe(self):
        return (self._name == 'Ubuntu' and self.expected_id <= self.actual_id)


at_least_trusty = AtLeastUbuntu('trusty')
