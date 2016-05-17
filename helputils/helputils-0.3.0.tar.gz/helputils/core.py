import copy
import errno
import inspect
import logging
import logging.handlers
import os
import sys
import traceback
from difflib import SequenceMatcher
from subprocess import Popen, PIPE

red, yellow, normal, green = "\x1b[31m", "\x1b[33m", "\x1b[30m", "\x1b[32m"


class SetupLogger():
    """Logs to syslog and console with some format conveniences. Instantiating class here, because other functions in here are
       dependent on this logger. So import the instance log from here and don't create a new instance of SetupLogger unless you
       want to derive from it."""

    def __init__(self, verbose):
        logging.basicConfig(format='%(message)s')
        self.logger = logging.getLogger()  # Initializing Logger
        syslog_handler = logging.handlers.SysLogHandler('/dev/log')
        self.logger.addHandler(syslog_handler)  # Add SysLogHandler
        self.console_handler = logging.StreamHandler()
        self.logger.addHandler(self.console_handler)
        if verbose == "vvv":
            self.logger.setLevel(logging.DEBUG)
        elif verbose == "vv":
            self.logger.setLevel(logging.INFO)
        elif verbose == "v":
            self.logger.setLevel(logging.ERROR)

    def info(self, message, newline=0):
        """Automatically log the current function details."""
        if newline > 0:
            self.newline(newline)
        self.logger.info("(I) {0}".format(message))

    def error(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.error("{0}(E) {1} {2}{3}".format(red, func.co_name, message, normal))

    def warning(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.warning("{0}(W) {1} {2}{3}".format(yellow, func.co_name, message, normal))

    def debug(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.debug("{0}(D) {1} {2}{3}".format(green, func.co_name, message, normal))

    def newline(self, how_many_lines=1):
        for i in range(how_many_lines):
            self.logger.info('')


log = SetupLogger('vvv')


def rsync(src, dst, remote_host=None, exclude=list()):
    """Rsync wrapper with exclude and remote_host"""
    src = os.path.normpath(src)
    if remote_host:
        p1 = Popen(["rsync", "-avHAXx"] + exclude + [src, "{0}:{1}".format(remote_host, dst)], stdout=PIPE)
    else:
        p1 = Popen(["rsync", "-avHAXx"] + exclude + [src, dst], stdout=PIPE)
    log.info(p1.communicate())
    log.info(p1.returncode)
    if p1.returncode != 0:
        log.error("Rsync error. sendmail")


def is_number(s):
    """Checks if given parameter is a number or not"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def find_mount_point(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path


def format_exception(e):
    """Usage:  except Exception as e: log.error(format_exception(e))"""
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    exception_str = exception_str[:-1]  # Removing the last \n
    return exception_str


def listdir_fullpath(d):
    """List dirs in given director with their fullpath."""
    return [os.path.join(d, f) for f in os.listdir(d)]


def try_func(func, args, kwargs):
    """Try except wrapper."""
    try:
        val = func(*args, **kwargs)
        return val
    except Exception as e:
        log.error(format_exception(e))
        return None


def similar(a, b):
    """Returns float from 0 to 1 of how similar two strings are."""
    return SequenceMatcher(None, a, b).ratio()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            log.error("Could not create directory")
            raise


def umount(mp, lazy=False):
    """Umounts given mountpoint. Can umount also with lazy switch."""
    cmd_mount, cmd_lazy_umount = (["umount"], ["umount", "-l"])
    cmd = cmd_lazy_umount if lazy else cmd_umount
    p1 = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    log.info(out, err)
    log.info("Unmounted encfs")


def mount(dev, mp):
    """Mounts a dev to mountpoint. If mp is occupied it'll try to umount first."""
    if os.path.ismount(mp):
        log.warning("Already mounted. Trying to unmount.")
        umount(mp)
        if os.path.ismount(mp):
            log.warning("Still mounted. Trying lazy unmount.")
            umount(mp, lazy=True)
            if os.path.ismount(mp):
                log.error("Couldn't be unmounted.")
                return False
    cmd_mount = ["mount", dev, mp]
    p1 = Popen(cmd_mount, stdin=PIPE)
    out, err = p1.communicate()
    if p1.returncode != 0 or not os.path.ismount(mount_dir):
        log.error("Mounting failed. Error: %s\n%s" % (out, err))
        return False
    else:
        log.info("Mounted %s to %s" (dev, mp))
        return True
