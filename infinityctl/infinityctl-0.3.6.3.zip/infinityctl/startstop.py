import subprocess
import sys
import glob
import os
import signal

from .config import Config
from .util import get_and_check_config, print_status


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
    subprocess.call(["DreamDaemon", dmb[0], str(config.port), '-trusted', '-logself'], shell=False, cwd=folder)


def stop(args):
    pid = int(get_pid('DreamDaemon'))
    os.kill(pid, signal.SIGTERM)

