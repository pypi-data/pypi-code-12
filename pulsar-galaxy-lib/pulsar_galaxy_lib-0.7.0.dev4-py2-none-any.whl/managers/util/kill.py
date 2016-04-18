import os
from platform import system
from time import sleep
from subprocess import Popen

try:
    from psutil import Process, NoSuchProcess
except ImportError:
    """ Don't make psutil a strict requirement, but use if available. """
    Process = None


def kill_pid(pid, use_psutil=True):
    if use_psutil and Process:
        _psutil_kill_pid(pid)
    else:
        _stock_kill_pid(pid)


def _psutil_kill_pid(pid):
    """
    http://stackoverflow.com/questions/1230669/subprocess-deleting-child-processes-in-windows
    """
    try:
        parent = Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except NoSuchProcess:
        return


def _stock_kill_pid(pid):
    is_windows = system() == 'Windows'

    if is_windows:
        __kill_windows(pid)
    else:
        __kill_posix(pid)


def __kill_windows(pid):
    try:
        Popen("taskkill /F /T /PID %i" % pid, shell=True)
    except Exception:
        pass


def __kill_posix(pid):
    def __check_pid():
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    if __check_pid():
        for sig in [15, 9]:
            try:
                os.killpg(pid, sig)
            except OSError:
                return
            sleep(1)
            if not __check_pid():
                return
