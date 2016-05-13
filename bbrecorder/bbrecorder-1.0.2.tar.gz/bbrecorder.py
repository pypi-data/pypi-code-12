#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""\
About bbrecorder
----------------

:author: Laurent Pointal <laurent.pointal@limsi.fr> <laurent.pointal@laposte.net>
:organization: CNRS - LIMSI
:copyright: CNRS - 2015
:license: New BSD License
:version: 1.0.2

This system is an intermediate spool keeping a limited set of last log records, and calling
other handlers with these log records in case of problem.
It allows to not fill log files, to not spend too much time in logging… but to be able to
retrieve complete up-to-date information in case of exception raising.

It is composed of a main :class:`BlackBoxHandler` logging handler class, managing the
spool, which must be associated to normal logging handlers using its
:any:`add_sub_handler()` method.
The box size can be modified via :any:`set_size()` method (it is initially
set to store 200 log records).

When a situation require the dump of black box logging content, a call to the
:func:`crisis` function (module level, proceed with all black boxes) or to a specific
box :any:`crisis_emit()` method make the box(es) dump their stored logs
using associated standard log handlers.

Usage example::

    import bbrecorder
    import logging

    # Create the logger.
    logger = logging.getLogger("bbtest")
    logger.setLevel(logging.DEBUG)

    # Create BlackBoxHandler and relative logging stuff.
    box = bbrecorder.BlackBoxHandler()
    box.set_size(10)
    fh = logging.FileHandler('_testresult.log')
    ch = logging.StreamHandler()
    box.add_sub_handler(fh)
    box.add_sub_handler(ch)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    box.setFormatter(formatter)

    # Associate BlackBoxHandler with our logger.
    logger.addHandler(box)

    lst = []
    for i in range(1000):
        lst.append(i)
        logger.debug('This %d message should go to the log file with %s', i, lst)
        if len(lst)>=7:
            lst = []

    # Here, we should only get the last 10 logs, with the value of lst corresponding to the
    # time logs ware created. This is typically called within an exception handler.
    bbrecorder.crisis()


The module level :func:`full_install` function setup en environment where it
logs Python crashes and allows user to trig black box log emitting via the
:kbd:`Ctrl-C` key combination and other signals.

.. important::

    For applications which may hardly crash within low level C Python code,
    inside a compiled extension module, when calling a native function via
    ctypes… with invalid args, etc.
    You must look at `faulthandler <https://docs.python.org/3/library/faulthandler.html>`_
    standard module and use it to retrieve tracebacks for threads::

        import faulthandler
        # Create a special file.
        outfile = open("python_faulthandler.txt", "w")
        # Enable the fault handler for the SIGSEGV, SIGFPE, SIGABRT, SIGBUS and SIGILL
        faulthandler.enable(outfile)

    Because generating logs via a BlackBoxHandler may make them loosed if a hard
    Python crash occur.
    
    Note that this Python faulthandler tool module appear with Python 3.3, and has
    not been backported (yet) to Python 2.7.

.. note::

    The module has been tested with Python 3.4 and 3.5, and made compatible with Python 2
    and tested on Python 2.7  for version 1.0.2.
    
"""

__all__ = [
    'BlackBoxHandler',
    'crisis',
    'crisis_signal',
    'full_install',
    ]

# Debug of this module.
DEBUG = True

import logging
try:
    import threading
    _boxes_lock = threading.Lock()
except:
    threading = None
import weakref
import signal

# How many log records to keep by default.
INITIAL_BOX_SIZE = 200

# We keep a list of weak refs to created boxes to be able call their crisis_emit() method.
_boxes_wr = []


class BlackBoxHandler(logging.Handler):
    """\
    Specific logging handler to store in memory a limited (rotation of) logs.

    By default the black box handler will keep last :const:`INITIAL_BOX_SIZE` (200) log records.
    You can change this value using :func:`set_size` method.

    Once you created a :class:`BlackBoxHandler`, you must associate some logging handlers to it
    with its :func:`add_sub_handler` method.
    Unless you specify a formatter for these sub handlers, they will use same formatter as the
    black box one.

    When you encounter a situation where you want to store/display recent stored log records,
    you can call general :func:`crisis` function, to extract logs from all black boxes,
    or call a specific black box :func:`crisis_emit` method.

    .. warning::

        By default log records msg is immediately formatted with its args, which are then dismissed.
        Two benefits:

        - mutable args are formatted with the value they have at log record creation time.

        - args are not keep during all life time of the record in the blackbox.

        You may delay this formatting calling :func:`set_dismiss_record_args` method with
        :const:`False`… but care with delayed logs generation consequences vs mutable
        formatting parameters.

    :ivar int _boxsize: maximum count of last logs stored, default to 200.
    :ivar bool _dismiss_record_args: indicator to format log msg with args immediately then dismiss them,
        default to True.
    :ivar list _records: storage of most recent log records.
    :ivar list _sub_handlers: handlers to use in case of crisis_emit. All these sub handlers will use the
        black box filters and formatter, they are directly used to emit the log records.
    """
    def __init__(self, **args):
        super(BlackBoxHandler, self).__init__(**args)
        self._boxsize = INITIAL_BOX_SIZE
        self._dismiss_record_args = True
        self._records = []      # Dont use a queue as we remove older items to limit to _boxsize length.
        self._sub_handlers = []

        # Setup a default formatter other than the logging global one.
        self.setFormatter(logging.Formatter())

        # Reference the box.
        _refbox(self)

    def close(self):    # Override.
        # Ensure sub handlers are closed.
        try:
            self.acquire()
            for sh in self._sub_handlers:
                sh.close()
            self._sub_handlers[:] = []     # N longer use
        finally:
            self.release()

    def setFormatter(self, fmt):    # Override
        # Propagate formatter to sub handlers having no formatter or same formatter.
        try:
            self.acquire()
            for sh in self._sub_handlers:
                if sh.formatter is None or sh.formatter is self.formatter:
                    sh.setFormatter(fmt)
            super(BlackBoxHandler, self).setFormatter(fmt)
        finally:
            self.release()

    def emit(self, record):     # Override.
        # Note: lock is acquired within handle when emit is called.
        if not self._boxsize:
            return

        if self._dismiss_record_args:
            record.msg = record.getMessage()     # Cache the result in msg.
            record.args = ()        # Avoid re-formatting.

        self._records.append(record)
        if len(self._records) > self._boxsize:
            self._records.pop(0)

    def set_size(self, size):
        """\
        Modify the count of log records stored by the black box handler.

        :param int size: new maximum count of log records to keep.
        """
        assert(size >= 0)        # Debug mode
        if size < 0: size = 0  # Normal running mode

        try:
            self.acquire()
            if size < len(self._records):
                # Must loose older records
                del self._records[0:len(self._records)-size]
            self._boxsize = size
        finally:
            self.release()

    def set_dismiss_record_args(self, dismiss=True):
        """\
        Modify the dismiss record args flag to do immediate log record msg format and dimiss args.

        :param bool dismiss: new flag value.
        """
        self._dismiss_record_args = dismiss

    def add_sub_handler(self, handler):
        """\
        Add a logging handler to be used to transmit / store / display log records in crisis_emit situation.

        :param logging.Handler handler:
        :return:
        """
        try:
            self.acquire()
            if handler in self._sub_handlers:
                return
            self._sub_handlers.append(handler)
            if handler.formatter is None:
                handler.setFormatter(self.formatter)
        finally:
            self.release()

    def crisis_emit(self):
        """\
        Ensure transmission / storage / display of recent log records via the sub handlers
        installed by :any:`add_sub_handler()` method calls.

        Once done, log records storage is cleared (so logs won't be written multiple times by
        the same box).
        """
        try:
            self.acquire()
            if not self._records:
                return
            for sh in self._sub_handlers:
                # Note: must acquire sub handler's lock as it is done when calling emit() by logging system.
                # Take advantage of emitting a sequence of records to just acquire once.
                try:
                    sh.acquire()
                    for record in self._records:
                        sh.emit(record)
                    sh.flush()    # Ensure writing.
                finally:
                    sh.release()
            self._records[:] = []
        finally:
            self.release()


def _refbox(box):
    """\
    Add global weak reference to a box handler.

    :param BlackBoxHandler box: box handler to reference globally.
    """
    try:
        if threading:
            _boxes_lock.acquire()
        _boxes_wr.append(weakref.ref(box, _unrefbox))
    finally:
        if threading:
            _boxes_lock.release()


def _unrefbox(box):
    """\
    Remove global weak reference to a box handler.

    :param BlackBoxHandler box: weak ref of box handler to unreference.
    """
    try:
        if threading:
            _boxes_lock.acquire()
        if box in _boxes_wr:
            _boxes_wr.remove(box)
    finally:
        if threading:
            _boxes_lock.release()


def crisis():
    """\
    Dump black box log records, called in crisis situation (exception…).

    You must call this function when you are interested to emit currently stored log records to
    normal handlers (file, syslog, etc).
    The function loop over created :class:`BlackBoxHandler` objects and call their respective
    :any:`crisis_emit()` methods.

    The :func:`crisis_signal` function provides same service callable as a
    `signal handler <https://docs.python.org/3/library/signal.html>`_ .
    """
    try:
        if threading:
            _boxes_lock.acquire()
        for boxwr in _boxes_wr:
            box = boxwr()      # Get object from weak reference.
            if box is not None:
                box.crisis_emit()
    finally:
        if threading:
            _boxes_lock.release()


_prev_signals = {}
def crisis_signal(signum, stackframe):
    """\
    Callback function to be installed as signal handler (see
    `Python signal module <https://docs.python.org/3/library/signal.html>`_).
    """
    try:
        crisis()
    except:
        pass
    if signum in _prev_signals:
        _prev_signals[signum](signum, stackframe)


def signal_install(signum, chain=True):
    """\
    Install a :func:`crisis_signal` handler for signum.

    :param int signum: signal number to handle.
    :param bool chain: flag to require call of existing signal handler after crisis one.
    """
    if chain:
        _prev_signals[signum] = signal.getsignal(signum)
    signal.signal(signum, crisis_signal)


def full_install():
    """\
    Install services to catch / trace hard errors from the Python application.

    Intercept keyboard breaks to dump black boxes log records.
    """
    for signame, chain in [('SIGINT', True),        # Triggered by Ctrl-C
                            ('SIGTERM', True),      # External termination request
                            ('SIGQUIT', True),      # Terminal request to quit (and core-dump).
                            ('SIGINFO', False),     # Triggered by Ctrl-T sometimes
                            ('CTRL_C_EVENT', True), # Triggered by Ctrl-C on Windows
                            ('CTRL_BREAK_EVENT', True),
                            ]:
        if hasattr(signal, signame):
            signum = getattr(signal, signame)
            signal_install(signum, chain)
