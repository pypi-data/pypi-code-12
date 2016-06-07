# Copyright (C) 2016 Cisco Systems, Inc. and/or its affiliates. All rights reserved.
#
# This file is part of Katnip.
#
# Katnip is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Katnip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Katnip.  If not, see <http://www.gnu.org/licenses/>.
'''
Apple's CrashWrangler wrapper for python.
This code assumes you already have crashwrangler installed on your system.
You can download crashwrangler here:
https://developer.apple.com/library/mac/technotes/tn2334/_index.html
'''
from subprocess import Popen, PIPE
import os
import time


class CrashWrangler(object):

    def __init__(self, cw_exe='./exc_handler'):
        self.cw_exe = cw_exe
        self.env = {k: v for (k, v) in os.environ.items()}
        self.cw_proc = None

    def start_proc(self, proc, args):
        cmd = [self.cw_exe, proc] + args
        self.cw_proc = Popen(cmd, stdout=PIPE, stderr=PIPE, env=self.env)
        return (self.cw_proc.stdout, self.cw_proc.stderr)

    def stop_proc(self):
        if self.cw_proc is None:
            raise Exception('No process is running')
        if self._process.poll() is None:
            self.cw_proc.terminate()
            time.sleep(0.5)
        if self._process.poll() is None:
            self.cw_proc.kill()
            time.sleep(0.5)
        if self._process.poll() is None:
            raise Exception('Failed to kill process')
        return self._process.returncode
