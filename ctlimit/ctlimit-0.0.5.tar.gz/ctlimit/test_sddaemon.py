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
import logging
import sys
import io
import os
import fixtures
import tempfile

from ctlimit import sddaemon

DEFAULT_CONFIGURATION = """
[ConfigFiles]
status_file = /dev/null

# regular config files
# config_file0 is not configurable, because it is this file
config_file1: ${common:config_file}
config_file2: ${status_file}
config_on_failure1: warn
config_on_failure2: ignore

############ LOGGING ############

[loggers]
keys=root

[handlers]
keys=sd_daemon

[formatters]
keys=sd_daemon

[logger_root]
# level=NOTSET
level=${common:log_level}
handlers=sd_daemon

[handler_sd_daemon]
class=StreamHandler
level=DEBUG
formatter = sd_daemon
args=(sys.stderr,)

[formatter_sd_daemon]
format=%(levelname)s: %(message)s
class=ctlimit.SdDaemonLoggingFormatter

############ internal stuff ############

# an internal section
[__saved_state__]

""".splitlines(True)

CONFIG_FILE_CONTENT = "# empty"


class TextFileFixture(fixtures.Fixture):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def _setUp(self):
        super()._setUp()
        self.useFixture(fixtures.NestedTempfile())
        with tempfile.NamedTemporaryFile(mode="wt", encoding="utf-8", delete=False) as fp:
            self.path = fp.name
            self.addCleanup(os.unlink, self.path)
            fp.write(self.content)


class EventDrivenDaemonTest(fixtures.TestWithFixtures):

    def setUp(self):
        super().setUp()
        configfile = TextFileFixture(CONFIG_FILE_CONTENT)
        self.useFixture(configfile)

        daemon = sddaemon.EventDrivenDaemon()
        daemon.DEFAULT_CONFIG_FILE = DEFAULT_CONFIGURATION

        daemon.setup_configuration(configfile.path, 2)
        self.daemon = daemon

    def testLoadConfig(self):
        self.assertIsInstance(self.daemon.config, configparser.ConfigParser)

    def testLogging(self):
        self.daemon.configure_sd_daemon_logging()
        root = logging.getLogger()
        self.assertEqual(len(root.handlers), 1)
        handler = root.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        stream = handler.stream
        self.assertIs(stream, sys.stderr)
        self.addCleanup(setattr, handler, "stream", stream)
        handler.stream = stringio = io.StringIO()
        root.error("line1\nline2")
        msg = stringio.getvalue()
        self.assertEqual(msg, "<3>ERROR: line1\n<3>    line2\n")


if __name__ == "__main__":
    unittest.main()
