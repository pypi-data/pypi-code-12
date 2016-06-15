# Copyright 2016 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Fixture for managing test daemon processes."""

import os
import time
import signal

from fixtures import (
    Fixture,
)

from testtools.content import (
    Content,
    )
from testtools.content_type import UTF8_TEXT

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


class DaemonFixture(Fixture):
    """Start and stop a daemon process."""

    def __init__(self, command, env=None, is_ready=None, timeout=15):
        """
        @param command: A list or tuple with the daemon executable and command
            line arguments. It will be passed to subprocess.Popen.
        @param env: Optionally, the environment to use when spawning the daemon
            process.
        @param is_ready: Optionally, a callable that should return True if the
            daemon is ready and operational, False otherwise. The fixture setUp
            will poll this callable until it returns True.
        @param timeout: Maximum time to wait for starting or stopping the
            daemon, before taking extreme measures like raising an exception or
            killing the process.
        """
        super(DaemonFixture, self).__init__()
        self._command = command
        self._env = env
        self._process = None
        self._is_ready = is_ready
        self._timeout = timeout

    def is_running(self):
        """Whether the daemon process still running."""
        if self._process is None:
            return False
        else:
            return self._process.poll() is None

    def kill(self):
        """Kill the daemon server process.

        This will send a SIGKILL to the daemon process and its children, it is
        used as last resort to terminate the process.

        It is also useful to test your code against scenarios where the daemon
        dies.
        """
        self._signal(signal.SIGKILL)
        time.sleep(0.5)
        if self.is_running():
            raise Exception("Daemon process just won't die.")

    def _setUp(self):
        self._start()

    def _start(self):
        """Start the daemon process."""
        self._spawn()
        if self._is_ready:
            timeout = time.time() + self._timeout
            while time.time() < timeout and self.is_running():
                if self._is_ready():
                    break
                time.sleep(0.3)
            else:
                self.kill()
                raise Exception("Timeout waiting for daemon process to start")
        self.addCleanup(self._stop)

    def _spawn(self):
        """Spawn the daemon process."""
        self._process = subprocess.Popen(
            self._command, env=self._env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, preexec_fn=_preexec_fn)

    def _stop(self):
        """Stop the daemon process, possibly killing it."""
        timeout = time.time() + self._timeout
        try:
            self._request_stop()
            if self._is_ready:
                while time.time() < timeout:
                    if not self._is_ready():
                        break
                    time.sleep(0.3)
                else:
                    raise Exception(
                        "Timeout waiting for the daemon node to go down.")
        except subprocess.TimeoutExpired:
            # Go straight to killing the process directly.
            timeout = time.time()

        # Wait at least 5 more seconds for the process to end...
        timeout = max(timeout, time.time() + 5)
        while time.time() < timeout:
            if not self.is_running():
                break
            self._signal(signal.SIGTERM)
            time.sleep(0.1)
        else:
            # Die!!!
            if self.is_running():
                self.kill()

    def _request_stop(self):
        """Try to stop the daemon cleanly."""
        self._process.terminate()
        self._process.wait(timeout=self._timeout)
        outstr, errstr = self._process.communicate()
        binary = self._command[0].split("/")[-1]
        if outstr:
            self.addDetail(
                '%s-out' % binary, Content(UTF8_TEXT, lambda: [outstr]))
        if errstr:
            self.addDetail(
                '%s-err' % binary, Content(UTF8_TEXT, lambda: [errstr]))

    def _signal(self, code):
        """Send a signal to the daemon process and all its children."""
        os.killpg(os.getpgid(self._process.pid), code)


def _preexec_fn():
    # Create a new process group, so we can send signals to both
    # the process we spawn an and its possible child processes.
    os.setsid()
