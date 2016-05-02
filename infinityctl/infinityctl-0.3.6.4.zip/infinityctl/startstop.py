import subprocess
import sys
import glob
import os
import signal

from .config import Config
from .util import get_and_check_config, print_status


def spawn_daemon(port, dmb):
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # parent process, return and keep running
            return
    except OSError:
        sys.exit(1)

    os.setsid()

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError:
        sys.exit(1)

    subprocess.call(["DreamDaemon", dmb, port, '-trusted', '-logself'], shell=False, cwd=folder)

    # all done
    os.exit(os.EX_OK)


# получить PID процесса. только Unix-системы
def get_pid(name):
    return subprocess.check_output(["pidof",name])


def start(args):
    config = get_and_check_config(args)
    build = config.get_build(args.build)
    folder = config.basedir + build.get('folder')

    dmb = glob.glob(folder + "/*.dmb")
    if not dmb:
        print("Билд не скомпилирован")
        sys.exit(1)
    spawn_daemon(str(config.port), dmb[0])



def stop(args):
    pid = int(get_pid('DreamDaemon'))
    os.kill(pid, signal.SIGTERM)

