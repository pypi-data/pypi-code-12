#!/bin/env python
# -*- coding: utf-8 -*-

import os
import grp
import time
import signal
import daemon
import lockfile

import include
from dockerfly.settings import dockerfly_version, LOCK_TIMEOUT, DAEMON_PROCESS_COUNT
from dockerfly.settings import VAR_ROOT, LOG_ROOT, DB_ROOT, RUN_ROOT
from dockerfly.contrib.filelock import FileLock

if not os.path.exists(VAR_ROOT):
    os.makedirs(VAR_ROOT)
if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)
if not os.path.exists(DB_ROOT):
    os.makedirs(DB_ROOT)
if not os.path.exists(RUN_ROOT):
    os.makedirs(RUN_ROOT)

from dockerfly.logger import getLogger, getFh
from dockerfly.http.server import run_server

PIDFILE = FileLock(os.path.join(RUN_ROOT, 'dockerflyd.pid.lock'))
logger = getLogger()

def dockerflyd_setup():
    if PIDFILE.is_locked:
        logger.error("{} has already existed".format(PIDFILE.lock_file))
    else:
        PIDFILE.acquire(timeout=LOCK_TIMEOUT)

def dockerflyd_cleanup():
    if PIDFILE.is_locked:
        PIDFILE.release()

def dockerflyd_reload_config():
    pass

def terminate():
    os.kill(os.getpid(), signal.SIGTERM)

context = daemon.DaemonContext(
    working_directory=RUN_ROOT,
    umask=0o002,
    pidfile=PIDFILE,
    files_preserve = [getFh().stream,],
)

context.signal_map = {
    signal.SIGTERM: dockerflyd_cleanup,
    signal.SIGHUP: terminate,
    signal.SIGUSR1: dockerflyd_reload_config,
    }

mail_gid = grp.getgrnam('mail').gr_gid
context.gid = mail_gid

def rundaemon(host, port):
    dockerflyd_setup()

    with context:
        run_server(host=host, port=port, debug=True, process=DAEMON_PROCESS_COUNT)
        #dirty wait for all process running
        time.sleep(10)

if __name__ == '__main__':

    rundaemon(host='0.0.0.0', port=5123)

