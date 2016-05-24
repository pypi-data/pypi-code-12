
import threading
import logging
import os
import sys
import weakref
import select
import time


import wayround_org.utils.path
import wayround_org.utils.stream
import wayround_org.utils.time
import wayround_org.utils.error
import wayround_org.utils.osutils
import wayround_org.utils.weakref
import wayround_org.utils.socket


class _LoggingFileLikeObject:
    """
    this class shoultd not be used by outsiders
    """

    def __init__(self, log_instance, typ='info'):

        if typ not in ['info', 'error']:
            raise ValueError("invalid typ value")

        self._log = log_instance
        self._typ = typ
        # self._pipe = os.pipe2(os.O_NONBLOCK)
        self._pipe = os.pipe()
        self._pipe_read_file = open(
            self._pipe[0],
            mode='r',
            # buffering=0,
            # closefd=False
            closefd=True
            )

        self._sync_out_lock = threading.Lock()

        self._stop_flag = threading.Event()

        _t1 = threading.Thread(
            name="_thread_run thread of {}".format(self),
            target=self._thread_run
            )
        _t1.start()

        self._thread = _t1

        return

    def fileno(self):
        return self._pipe[1]

    def stop(self):
        self._stop_flag.set()
        return

    def _thread_run(self):

        while True:

            if self._stop_flag.is_set():
                break

            sel_res = select.select([self._pipe_read_file], [], [], 0.5)[0]

            if self._stop_flag.is_set():
                break

            if len(sel_res) == 0:
                continue

            try:
                line = self._pipe_read_file.readline()
            except OSError:
                logging.exception("error")
                continue

            with self._sync_out_lock:

                if self._stop_flag.is_set():
                    break

                #line = str(line, 'utf-8')
                line = line.rstrip('\n\r\0')

                if self._typ == 'info':
                    self._log.info(line)

                if self._typ == 'error':
                    self._log.error(line)

        threading.Thread(target=self.stop).start()

        self._pipe_read_file.close()

        try:
            os.close(self._pipe[1])
        except OSError:
            pass

        try:
            os.close(self._pipe[0])
        except OSError:
            pass

        return


class LogStrong:

    """
    This class requires .close() calling for log to be stopped.
    Use Log for log which allows close using garbage collector.
    """

    def __init__(
            self,
            log_dir,
            logname,
            echo=True,
            timestamp=None,
            longest_logname=None,
            group=None,
            user=None
            ):

        ret = 0
        self.code = 0
        # self.fileobj = None
        self.logname = logname
        self.log_filename = None
        self.longest_logname = longest_logname
        self._write_lock = threading.Lock()
        self._stop_lock = threading.Lock()

        # TODO: attributes cleanups may be required

        self._stop_called_once = False

        # TODO: group and user parameter's behavior need to be improved
        self._group, self._user = wayround_org.utils.osutils.convert_gid_uid(
            group,
            user
            )

        self.stdout = _LoggingFileLikeObject(self, 'info')
        self.stderr = _LoggingFileLikeObject(self, 'error')

        os.makedirs(log_dir, exist_ok=True)

        if (not os.path.isdir(log_dir)
            or os.path.islink(log_dir)
            ):
            logging.error(
                "Current file type is not acceptable: {}".format(
                    log_dir
                    )
                )
            ret = 2

        if ret == 0:
            if self._user is not None and self._group is not None:
                os.chown(
                    log_dir,
                    self._user,
                    self._group
                    )

        if ret == 0:

            if timestamp is None:
                timestamp = wayround_org.utils.time.currenttime_stamp_iso8601()

            self.filename = wayround_org.utils.path.abspath(
                os.path.join(
                    log_dir,
                    "{ts:26} {name}.txt".format(
                        name=logname,
                        ts=timestamp
                        )
                    )
                )

            self.log_filename = self.filename

            self.info(
                "[{}] log started" .format(
                    self.logname
                    ),
                echo=echo,
                timestamp=timestamp
                )

        if ret == 0:
            if self._user is not None and self._group is not None:
                os.chown(
                    self.log_filename,
                    self._user,
                    self._group
                    )

        if ret != 0:
            raise Exception("Exception during Log creation. read above.")

        return

    def stop(self, echo=True):

        with self._stop_lock:

            if not self._stop_called_once:

                self._stop_called_once = True

                # if self.fileobj is not None:
                timestamp = \
                    wayround_org.utils.time.currenttime_stamp_iso8601()

                self.info(
                    "[{}] log ended" .format(
                        self.logname
                        ),
                    echo=echo,
                    timestamp=timestamp
                    )

                if self.stdout is not None:
                    self.stdout.stop()

                if self.stderr is not None:
                    self.stderr.stop()

                self.stdout = None
                self.stderr = None

                # self.fileobj.flush()
                # self.fileobj.close()
                #self.fileobj = None

        return

    close = stop

    def write(self, text, echo=False, typ='info', timestamp=None):

        if typ not in ['info', 'error', 'exception', 'warning']:
            raise ValueError("Wrong `typ' parameter")

        # if self.fileobj is None:
        #    raise Exception("Log output file object is None")

        if timestamp is not None:
            pass
        else:
            timestamp = wayround_org.utils.time.currenttime_stamp_iso8601()

        log_name = self.logname
        if self.longest_logname is not None:
            log_name += ' ' * (self.longest_logname - len(self.logname) - 1)

        icon = 'i'
        if typ == 'info':
            icon = 'i'
        elif typ == 'error':
            icon = 'e'
        elif typ == 'exception':
            icon = 'E'
        elif typ == 'warning':
            icon = 'w'
        else:
            icon = '?'

        msg2 = "[{}] [{:26}] [{}] {}".format(
            icon,
            timestamp,
            log_name,
            text
            )

        msg2_scn = "\033[0;1m[{}] [{:26}] [{}]\033[0m {}".format(
            icon,
            timestamp,
            log_name,
            text
            )

        if icon != 'i':
            msg2_scn = (
                "\033[0;1m[\033[0m\033[0;4m\033"
                "[0;5m{}\033[0m\033[0;1m] [{:26}] [{}]\033[0m {}".format(
                    icon,
                    timestamp,
                    log_name,
                    text
                )
                )

        with self._write_lock:
            with open(self.filename, 'a') as fileobj:
                fileobj.write(msg2 + '\n')
                fileobj.flush()
                fileobj.close()
            if echo:
                sys.stderr.write(msg2_scn + '\n')
                sys.stderr.flush()
        return

    def error(self, text, echo=True, timestamp=None):
        self.write(text, echo=echo, typ='error', timestamp=timestamp)
        return

    def exception(self, text, echo=True, timestamp=None, tb=True):
        ei = wayround_org.utils.error.return_instant_exception_info(
            tb=tb
            )
        ttt = """\
{text}
{ei}
""".format(text=text, ei=ei)

        self.write(ttt, echo=echo, typ='exception', timestamp=timestamp)
        return

    def info(self, text, echo=True, timestamp=None):
        self.write(text, echo=echo, typ='info', timestamp=timestamp)
        return

    def warning(self, text, echo=True, timestamp=None):
        self.write(text, echo=echo, typ='warning', timestamp=timestamp)
        return


global_log_storage = {}


class Log:

    def __init__(self, *args, **kwargs):
        self._own_id = id(self)
        global_log_storage[self._own_id] = LogStrong(*args, **kwargs)
        return

    def __del__(self):
        global_log_storage[self._own_id].stop()
        del global_log_storage[self._own_id]
        return

    def _proxy_call(self, function, *args, **kwargs):
        attr = getattr(global_log_storage[self._own_id], function, None)
        if attr is not None:
            ret = attr(*args, **kwargs)
        else:
            raise KeyError(
                "object {} has no attr {}".format(self, function)
                )
        return ret

    @property
    def stdout(self):
        return getattr(global_log_storage[self._own_id], 'stdout', None)

    @property
    def stderr(self):
        return getattr(global_log_storage[self._own_id], 'stderr', None)

    def stop(self, *args, **kwargs):
        return self._proxy_call('stop', *args, **kwargs)

    def write(self, *args, **kwargs):
        return self._proxy_call('write', *args, **kwargs)

    def error(self, *args, **kwargs):
        return self._proxy_call('error', *args, **kwargs)

    def exception(self, *args, **kwargs):
        return self._proxy_call('exception', *args, **kwargs)

    def info(self, *args, **kwargs):
        return self._proxy_call('info', *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._proxy_call('warning', *args, **kwargs)
