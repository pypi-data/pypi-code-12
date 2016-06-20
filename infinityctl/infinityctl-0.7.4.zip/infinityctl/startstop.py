import glob
import os
import signal
import subprocess
import sys

from .util import get_and_check_config


# получить PID процесса. только Unix-системы
def get_pid(name):
    return subprocess.check_output(["pidof",name])


def start(**args):
    config = get_and_check_config(args)
    build = config.get_build(args.get('build'))
    folder = config.basedir + build.get('folder')

    dmb = glob.glob(folder + "/*.dmb")
    if not dmb:
        print("Билд не скомпилирован")
        print("Каталог: {0}".format(folder))
        sys.exit(1)
    try:
        cpid = os.fork()
    except OSError:
        print("Не могу форкнуться :(")
    if cpid == 0:
        try:
            pid = subprocess.call(
                ['DreamDaemon', dmb[0], str(config.port), '-trusted', '-logself', '-public', '-threads on',
                 '-map-threads on'],
                shell=False,
                cwd=folder)
        except OSError:
            print('Не удалось запустить сервер')
        print('Сервер запущен, PID: {0}'.format(pid))
    sys.exit(0)


def stop(**args):
    pid = int(get_pid('DreamDaemon'))
    os.kill(pid, signal.SIGKILL)
