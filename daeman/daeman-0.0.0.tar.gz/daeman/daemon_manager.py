# -*- coding: utf-8 -*-

from __future__ import print_function

import signal
import os
from argparse import ArgumentParser
from daemon import DaemonContext
from daemon.pidfile import TimeoutPIDLockFile

class DaemonManager(object):
    def __init__(self, app, pid_path = None, stdin_path = None, stdout_path = None, stderr_path = None, workdir = '/'):
        self.app = app 
        self.pid_path = pid_path
        self.stdin_path = stdin_path
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        self.workdir = workdir

    def _get_desc(self, path, mode):
        return open(path, mode) if not (path is None) else None

    def _get_pid_desc(self, path):
        return TimeoutPIDLockFile(path) if not (path is None) else None

    def _get_pid(self, path):
        if (path is None):
            return None
        return TimeoutPIDLockFile(path).read_pid()

    def run(self):
        parser = ArgumentParser(description = '')
        parser.add_argument('-S', type = str, nargs = '?', default = 'start', choices = ['start', 'stop', 'restart'])
        args = parser.parse_args()
        self.dispatch(args.S)

    def dispatch(self, cmd):
        method = getattr(self, cmd, None)
        if (method is None):
            self.unknown_cmmand_error(cmd)
            return
        method()

    def start(self):
        pid_desc = self._get_pid_desc(self.pid_path)
        stdin_desc = self._get_desc(self.stdin_path, 'r')
        stdout_desc = self._get_desc(self.stdout_path, 'a')
        stderr_desc = self._get_desc(self.stderr_path, 'a')
        with DaemonContext(working_directory = self.workdir, pidfile = pid_desc, stdin = stdin_desc, stdout = stdout_desc, stderr = stderr_desc) :
            self.app.run()

    def stop(self):
        pid = self._get_pid(self.pid_path)
        if (pid is None):
            daemon_is_not_running_error()
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            pass

    def restart(self):
        self.stop_daemon()
        self.start_daemon()

    def unknown_command_error(self, cmd):
        print('unknown command:', cmd)

    def daemon_is_not_running_error(self):
        print('daemon is not running.')
