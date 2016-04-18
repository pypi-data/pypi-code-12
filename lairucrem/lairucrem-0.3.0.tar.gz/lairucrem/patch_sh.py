#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Module that patch python-sh"""

import os
import errno

import sh

from .utils import monkeypatch


#pylint: disable=bare-except
try:
    __sh__ = sh._SelfWrapper__self_module  # pylint: disable=protected-access
except:
    __sh__ = sh.self_module




@monkeypatch(__sh__.RunningCommand, 'next')
@monkeypatch(__sh__.RunningCommand)
def __next__(self):
    """ allow us to iterate over the output of our command """

    # we do this because if get blocks, we can't catch a KeyboardInterrupt
    # so the slight timeout allows for that.
    while True:
        try:
            chunk = self.process._pipe_queue.get(True, 0.001)  # pylint: disable=protected-access
        except __sh__.Empty:
            # start patch
            if not self.process.is_alive():
                self.wait()
                raise StopIteration()
            # end patch
            if self.call_args["iter_noblock"]:
                return errno.EWOULDBLOCK
        else:
            if chunk is None:
                self.wait()
                raise StopIteration()
            try:
                return chunk.decode(self.call_args["encoding"],
                                    self.call_args["decode_errors"])
            except UnicodeDecodeError:
                return chunk


# graft code from newer version of sh (1.11) we need but that is
# missing in older version (1.0.8 which is provided by Debian)

# pylint that's not my code. It shall be removed once Debian updates
#python-sh
#pylint: disable=protected-access
#pylint: disable=too-many-branches
#pylint:

if getattr(__sh__.OProc, 'is_alive', None) is None:
    def handle_process_exit_code(exit_code):
        """ this should only ever be called once for each child process """
        # if we exited from a signal, let our exit code reflect that
        if os.WIFSIGNALED(exit_code):
            return -os.WTERMSIG(exit_code)
        # otherwise just give us a normal exit code
        elif os.WIFEXITED(exit_code):
            return os.WEXITSTATUS(exit_code)
        else:
            raise RuntimeError("Unknown child exit status!")

    @monkeypatch(__sh__.OProc)
    def is_alive(self):
        """ polls if our child process has completed, without blocking.  this
        method has side-effects, such as setting our exit_code, if we happen to
        see our child exit while this is running """
        if self.exit_code is not None:
            return False
        acquired = self._wait_lock.acquire(False)
        if not acquired:
            if self.exit_code is not None:
                return False
            return True
        try:
            pid, exit_code = os.waitpid(self.pid, os.WNOHANG)
            if pid == self.pid:
                self.exit_code = handle_process_exit_code(exit_code)
                return False
        # no child process
        except OSError:
            return False
        else:
            return True
        finally:
            self._wait_lock.release()
