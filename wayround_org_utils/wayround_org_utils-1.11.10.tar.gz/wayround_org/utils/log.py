
import threading
import logging
import os
import io
import sys
import weakref
import select
import time
import atexit


import wayround_org.utils.path
import wayround_org.utils.stream
import wayround_org.utils.time
import wayround_org.utils.error
import wayround_org.utils.osutils
import wayround_org.utils.weakref
import wayround_org.utils.socket


class LoggingFileLikeObject:

    def __init__(self, log_instance, typ='info'):

        if not typ in ['info', 'error']:
            raise ValueError("invalid typ value")

        self._log = weakref.proxy(log_instance, self._on_log_finalize)
        self._typ = typ
        #self._pipe = os.pipe2(os.O_NONBLOCK)
        self._pipe = os.pipe()
        self._pipe_read_file = open(
            self._pipe[0],
            mode='r',
            # buffering=0,
            closefd=False
            )

        self._sync_out_lock = threading.Lock()

        self._stop_flag = threading.Event()

        _t1 = threading.Thread(
            name="_t1 thread of {}".format(self),
            target=self._thread_run
            )
        _t1.start()

        _t2 = threading.Thread(
            name="_t2 thread of {}".format(self),
            target=self._stop_flag_waiter_thread_func
            )
        _t2.start()

        self._thread = weakref.proxy(_t1)
        self._stop_flag_waiter_thread = weakref.proxy(_t2)

        return

    def __del__(self):
        self.stop()
        return

    def _on_log_finalize(self, ref):
        self.stop()
        return

    def _stop_flag_waiter_thread_func(self):
        while True:
            if self._stop_flag.is_set():
                break
            time.sleep(1)
        threading.Thread(target=self.stop).start()
        return

    def fileno(self):
        return self._pipe[1]

    def close(self):
        # NOTE: leaving this empty. this means what this object's thread
        #       should bot be stopped by file-like .close() method, nor by
        #       sending empty line into file descriptor.
        #       the only mean to sto thread here - should be self._stop_flag
        #       event
        return

    def stop(self):
        self._stop_flag.set()
        return

    def _thread_run(self):

        while True:

            if self._stop_flag.is_set():
                break

            sel_res = select.select([self._pipe_read_file], [], [], 0.5)[0]
            if len(sel_res) == 0:
                continue

            try:
                line = self._pipe_read_file.readline()
            except OSError:
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


class Log:
    """
    Note: this class does not uses stop() method to stop logging. Logging now
          stops automatically with object destruction.
          However, this means what .stdout and .stderr (which may be
          used as parameters for Popen) may be closed before Popen-ed
          application writes all it's stuff into them.

    Note: calling gc.collect() may be required at some points (perhaps at
          program end) to successfuly destroy threading objects created by Log
          for exiting Python interpreter normally.
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
        self.fileobj = None
        self.logname = logname
        self.log_filename = None
        self.longest_logname = longest_logname
        self._write_lock = threading.Lock()
        self._stop_lock = threading.Lock()

        # TODO: group and user parameter's behavior need to be improved
        self._group, self._user = wayround_org.utils.osutils.convert_gid_uid(
            group,
            user
            )

        self.stdout = LoggingFileLikeObject(self, 'info')
        self.stderr = LoggingFileLikeObject(self, 'error')

        self.stdout = weakref.proxy(self.stdout)
        self.stderr = weakref.proxy(self.stderr)

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

            filename = wayround_org.utils.path.abspath(
                os.path.join(
                    log_dir,
                    "{ts:26} {name}.txt".format(
                        name=logname,
                        ts=timestamp
                        )
                    )
                )

            self.log_filename = filename

            try:
                self.fileobj = open(filename, 'w')
            except:
                logging.exception("Error opening log file")
                ret = 3
            else:
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

    def __del__(self):
        self._stop()
        return

    def stop(self, echo=True):
        self._stop(echo=echo)
        return

    def close(self, *args, **kwargs):
        return self.stop(*args, **kwargs)

    def _stop(self, echo=True):

        with self._stop_lock:

            if self.fileobj is not None:
                timestamp = wayround_org.utils.time.currenttime_stamp_iso8601()
                self.info(
                    "[{}] log ended" .format(
                        self.logname
                        ),
                    echo=echo,
                    timestamp=timestamp
                    )

                self.stdout.stop()
                self.stderr.stop()

                self.stdout = None
                self.stderr = None

                self.fileobj.flush()
                self.fileobj.close()
                self.fileobj = None

        return

    def write(self, text, echo=False, typ='info', timestamp=None):

        if not typ in ['info', 'error', 'exception', 'warning']:
            raise ValueError("Wrong `typ' parameter")

        if self.fileobj is None:
            raise Exception("Log output file object is None")

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
            msg2_scn = "\033[0;1m[\033[0m\033[0;4m\033[0;5m{}\033[0m\033[0;1m] [{:26}] [{}]\033[0m {}".format(
                icon,
                timestamp,
                log_name,
                text
                )

        with self._write_lock:
            self.fileobj.write(msg2 + '\n')
            self.fileobj.flush()
            if echo:
                sys.stderr.write(msg2_scn + '\n')
                sys.stderr.flush()
        return

    def error(self, text, echo=True, timestamp=None):
        self.write(text, echo=echo, typ='error', timestamp=timestamp)
        return

    def exception(self, text, echo=True, timestamp=None, tb=True):
        # EXCEPTION TEXT:
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
