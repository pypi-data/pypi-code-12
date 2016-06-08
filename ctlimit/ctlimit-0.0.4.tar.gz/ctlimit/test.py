#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Esther Kruis and Anselm Kruis
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import unittest
import configparser
import fixtures

from ctlimit import _impl
from ctlimit.test_sddaemon import TextFileFixture

CONFIG_FILE_CONTENT = """
[DEFAULT]
seconds_per_day: 3600

[Users]
# a space separated list of names. For each word NAME in this list, ctlimit looks for a section named [NAME]
#
# Within the [USER]-sections, ctlimit looks for the following keys:
# name: the unix user name. If this key is not present, the section name is used instead
# seconds_per_day: the number of seconds computer time per day
#
users = esther master_of_the_universe

[master_of_the_universe]
name: anselm
seconds_per_day: 100

[ConfigFiles]
status_file = ${environ:HOME}/ctlimit.state
"""


class CtLimitDaemonTest(fixtures.TestWithFixtures):

    def setUp(self):
        super().setUp()

        self.useFixture(fixtures.TempHomeDir())
        configfile = TextFileFixture(CONFIG_FILE_CONTENT)
        self.useFixture(configfile)

        daemon = _impl.CtLimitDaemon()
        daemon.setup_configuration(configfile.path, 4)
        self.daemon = daemon

    def testLoadConfig(self):
        self.assertIsInstance(self.daemon.config, configparser.ConfigParser)


if __name__ == "__main__":
    unittest.main()
