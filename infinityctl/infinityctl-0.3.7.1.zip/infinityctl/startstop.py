import subprocess
import sys
import glob
import os
import signal

from .config import Config
from .util import get_and_check_config, print_status


# для запуска сервера завернем его в демон-обертку
def spawn_daemon(port, dmb, folder):
    # для надежности форкаемся два раза
    try:
        pid = os.fork()
        if pid > 0:
            # родительский процесс
            return
    except OSError:
        sys.exit(1)

    os.setsid()

    # второй форк
    try:
        pid = os.fork()
        if pid > 0:
            # завершение работы программы, она нам уже не нужна
            sys.exit(0)
    except OSError:
        sys.exit(1)

    # то, что будет запущено в дочернем процессе
    subprocess.call(["DreamDaemon", dmb, port, '-trusted', '-logself'], shell=False, cwd=folder)

    # all done
    print("Завершение работы сервера")
    sys.exit(0)


# получить PID процесса. только Unix-системы
def get_pid(name):
    return subprocess.check_output(["pidof",name])


def start(**args):
    config = get_and_check_config(args)
    build = config.get_build(args.build)
    folder = config.basedir + build.get('folder') + '/'

    dmb = glob.glob(folder + "/*.dmb")
    if not dmb:
        print("Билд не скомпилирован")
        sys.exit(1)
    spawn_daemon(str(config.port), dmb[0], folder)


def stop(args):
    pid = int(get_pid('DreamDaemon'))
    os.kill(pid, signal.SIGTERM)

