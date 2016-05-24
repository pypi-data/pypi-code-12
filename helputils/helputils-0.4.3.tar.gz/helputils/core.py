import copy
import errno
import inspect
import logging
import logging.handlers
import os
import socket
import sys
import traceback
from difflib import SequenceMatcher
from subprocess import Popen, PIPE


def _wrap_with(code):

    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner


red, green, yellow = _wrap_with('31'), _wrap_with('32'), _wrap_with('33')
blue, magenta, cyan, blue = _wrap_with('34'), _wrap_with('35'), _wrap_with('36'), _wrap_with('37')


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
        self.logger.error("{0}(E) {1}".format(func.co_name, red(message)))

    def warning(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.warning("{0}(W) {1}".format(func.co_name, (message)))
        self.logger.warning("{0}".format(cyan(message)))

    def debug(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.debug("{0}(D) {1}".format(func.co_name, magenta(message)))

    def newline(self, how_many_lines=1):
        for i in range(how_many_lines):
            self.logger.info('')


log = SetupLogger('vvv')


def isremotefile(f, hn=False):
    """Checks if file is a file, either locally or remotely."""
    cmd = ["file", "-b", f]
    if hn:
        cmd = ["ssh", hn] + cmd
    p1 = Popen(cmd, stdout=PIPE)
    out = p1.communicate()[0].decode("UTF-8")
    if "No such file" in out:
        return None
    elif "directory" in out:
        return False
    else:
        return True


def islocal(hn1):
    """Checks if the hostname is the local hostname"""
    hn2 = socket.gethostname()
    if hn1 in hn2 or hn2 in hn1:
        return True
    else:
        return False


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


def find_mountpoint(path, hn=False):
    """Returns mountpoint from local or given remote system (requires ssh alias for hostname to be configured)."""
    cmd = ["findmnt", "-T", path, "-n", "-o", "TARGET"]
    if hn:
        cmd = ["ssh", hn] + cmd
    p1 = Popen(cmd, stdout=PIPE)
    path = p1.communicate()[0].decode("UTF-8").strip()
    log.info("mountpoint is: %s" % path)
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


def remote_file_content(hn, fn):
    """Returns files content UTF-8 decoded via ssh by the given hostname and filename."""
    log.info("content of %s:%s (hn:filename)" % (hn, fn))
    p1 = Popen(["ssh", hn, "sudo", "/usr/bin/cat", fn], stdout=PIPE)
    return p1.communicate()[0].decode("UTF-8").split()


def try_func(func, *args, **kwargs):
    """Try except wrapper."""
    try:
        val = func(*args, **kwargs)
        return val
    except Exception as e:
        log.error(format_exception(e))
        return False


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
    cmd_umount, cmd_lazy_umount = (["/usr/bin/umount"], ["/usr/bin/umount", "-l"])
    cmd = cmd_lazy_umount if lazy else cmd_umount
    log.debug(cmd)
    p1 = Popen(cmd + [mp], stdout=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    log.info("umount: out: %s, err: %s" % (out, err))
    log.info("Unmounted mp %s" % mp)


def mount(dev, mp):
    """Mounts a dev to mountpoint. If mp is occupied it'll try to umount first."""
    if os.path.ismount(mp):
        log.warning("Already mounted. Trying to unmount.")
        umount(mp)
        if os.path.ismount(mp):
            log.warning("Still mounted. Trying lazy unmount.")
            try_func(umount, mp, lazy=True)
            if os.path.ismount(mp):
                log.error("Couldn't be unmounted.")
                return False
    cmd_mount = ["mount", dev, mp]
    try:
        p1 = Popen(cmd_mount, stdin=PIPE)
        out, err = p1.communicate()
        log.debug("out: %s, err: %s" % (out, err))
        if p1.returncode == 0 and os.path.ismount(mp):
            log.info("Mounted %s to %s" % (dev, mp))
            return True
        else:
            log.error("Mounting failed. Error: %s\n%s" % (out, err))
            return False
    except Exception as e:
        log.error(format_exception(e))
        return False
