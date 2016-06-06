
import copy
import logging
import threading
import time
import weakref

import wayround_org.utils.types
import wayround_org.utils.weakref


class Signal:

    def __init__(
            self,
            subject,
            signal_names=None,
            add_prefix=None,
            freezed=False,
            disabled=False,
            debug=False
            ):
        """
        Initiates Signal Functionality

        :param list signal_names: list of strings - signal names.

        If inheriting class or connecting entity will try to use wrong signal -
        ValueError will be raised
        """

        if signal_names is None:
            signal_names = []

        if not isinstance(signal_names, list):
            signal_names = [signal_names]

        if not wayround_org.utils.types.struct_check(
                signal_names,
                {'t': list, '.': {'t': str}}
                ):
            raise ValueError("`signal_names' must be None, str or list of str")

        self.subject = subject

        self._signals_debug = debug

        self._disabled = disabled

        self._signal_names = []

        self._signals = {}

        self._signal_subj_access_lock = threading.Lock()

        self.set_names(signal_names, add_prefix=add_prefix)

        self._emition_locking_event = threading.Event()
        self._emition_locking_event.set()
        self._emition_locking_counter = 0

        if freezed:
            self.freeze_emition()

        return

    def enable(self):
        self.set_disabled(False)
        return

    def disable(self):
        self.set_disabled(True)
        return

    def set_disabled(self, value):
        self._disabled = bool(value)
        if self._signals_debug:
            logging.debug(
                "{}: setting disabled to `{}'".format(
                    self.subject.__class__,
                    self._disabled
                    )
                )
        return

    def get_disabled(self):
        return bool(self._disabled)

    def freeze_emition(self):
        if self._emition_locking_counter == 0:
            self._emition_locking_event.clear()
        self._emition_locking_counter += 1
        return

    def unfreeze_emition(self):
        if self._emition_locking_counter == 0:
            raise Exception("output_lock_counter already 0")
        self._emition_locking_counter -= 1
        if self._emition_locking_counter == 0:
            self._emition_locking_event.set()
        return

    def set_names(self, signal_names=None, add_prefix=None):
        """
        Redefine acceptable signals

        NOTE: please understand simple rule: signals must be defined in
        object's creation time. This method (set_names) is provided only
        for completeness. So this method (set_names) must not be used in
        other places except object's class __init__! The reason for this rule
        is: if You will use this method in object's lifetime, then You will
        need to track changes in it's signal set, so things will become wired,
        hard and overheaded. For instance, SignalWaiter will not wait for new
        signals if it was created with signal_name=True (the connect() method
        param) and listened object changes own signal set, as SignalWaiter
        relies on this class'es connect for simplicity. Don't get things hard!
        """

        with self._signal_subj_access_lock:

            try:
                self._signal_names = _add_prefix(signal_names, add_prefix)

                for i in list(self._signals.keys()):
                    if not i in self._signal_names:
                        while i in self._signals:
                            del self._signals[i]

                for i in self._signal_names:
                    if not i in self._signals:
                        self._signals[i] = []

            except:
                logging.exception("Error setting signal_names")

        return

    def get_names(self, add_prefix=None):
        with self._signal_subj_access_lock:
            ret = _add_prefix(self._signal_names, add_prefix=add_prefix)
        return ret

    def _check(self, name):

        if not name in self._signal_names:
            raise ValueError(
                "{}: `{}' is not supported signal".format(self, name)
                )
        return

    def emit(self, name, *args, **kwargs):
        """
        Calls a callable attached to a signal with args and kwargs
        """

        if self._disabled:
            if self._signals_debug:
                logging.debug(
                    "{}: disabled. dropping {}, {}, {}".format(
                        self.subject.__class__,
                        name,
                        args,
                        kwargs
                        )
                    )
            return

        self._emition_locking_event.wait()

        with self._signal_subj_access_lock:

            try:

                self._check(name)

                if self._signals_debug:
                    logging.debug(
                        "({}) preparing emiting signal `{}'".format(
                            self.subject.__class__, name
                            )
                        )

                for i in self._signals[name][:]:

                    ref = i()

                    if not ref:
                        while i in self._signals[name]:
                            self._signals[name].remove(i)
                            if self._signals_debug:
                                logging.debug(
                                    "({}) removed garbage `{}' from `{}'".format(
                                        self.subject.__class__, i, name
                                        )
                                    )

                    else:

                        if self._signals_debug:

                            logging.debug(
                                "({}) emiting signal `{}'".format(
                                    self.subject.__class__, name
                                    )
                                )

                        threading.Thread(
                            name="{} :: Thread emiting signal `{}'".format(
                                self.subject.__class__, name
                                ),
                            target=ref,
                            args=(name,) + args,
                            kwargs=kwargs
                            ).start()
            except:
                logging.exception("Error emitting signal")

        return

    def connect(self, signal_name, callback):
        """
        Connect to some signal

        signal_name can be str, list of strings or True

        signal_name == True - means connect to all signals
        """

        with self._signal_subj_access_lock:

            try:

                if signal_name == True:
                    signal_name = self._signal_names

                if isinstance(signal_name, str):
                    signal_name = [signal_name]

                if isinstance(signal_name, list):

                    for i in signal_name:

                        self._check(i)

                        if not i in self.is_connected(
                                callback,
                                signal_name=i
                                ):

                            if wayround_org.utils.types.is_method(callback):
                                wr = wayround_org.utils.weakref.WeakMethod(
                                    callback, self._print_wr_deletion
                                    )
                            else:
                                wr = weakref.ref(callback)
                            self._signals[i].append(wr)

                            if self._signals_debug:

                                logging.debug(
                                    "({}) connected `{}' ({}) to `{}'".format(
                                        self.subject.__class__,
                                        callback,
                                        wr,
                                        i
                                        )
                                    )
                        else:

                            if self._signals_debug:

                                logging.debug(
                                    "({}) callbacl `{}' "
                                    "already connected to `{}'".
                                    format(
                                        self.subject.__class__,
                                        callback,
                                        i
                                    )
                                    )

            except:
                logging.exception("Error connecting signal")

        return

    def _print_wr_deletion(self, wr):

        if self._signals_debug:

            logging.debug(
                "({}) `{}' finalizes".format(
                    self.subject.__class__, wr
                    )
                )
        return

    def disconnect(self, callback, signal_name=None):
        """
        Disconnects callback from all signals or from certain signal
        """

        with self._signal_subj_access_lock:

            try:

                if signal_name:
                    if signal_name in self._signals:
                        while callback in self._signals[signal_name]:
                            self._signals[signal_name].remove(callback)

                            if self._signals_debug:
                                logging.debug(
                                    "({}) removed on "
                                    "request `{}' from `{}'".format(
                                        self.subject.__class__,
                                        callback,
                                        signal_name
                                        )
                                    )

                else:

                    for i in list(self._signals.keys()):
                        while callback in self._signals[i]:
                            self._signals[i].remove(callback)

                            if self._signals_debug:
                                logging.debug(
                                    "({}) removed on "
                                    "request `{}' from `{}'".format(
                                        self.subject.__class__,
                                        callback,
                                        i
                                        )
                                    )

            except:
                logging.exception("Error disconnecting signal")

        return

    def is_connected(self, callback, signal_name=None):

        ret = []

        if signal_name:
            if signal_name in self._signals:
                if callback in self._signals[signal_name]:
                    ret.append(signal_name)

        else:

            for i in list(self._signals.keys()):
                if callback in self._signals[i]:
                    ret.append(i)

        return ret

    def has_signal(self, name):
        return name in self._signal_names

    def gen_call_queue(self, name):
        return CallQueue.new_for_signal(None, self, name)


class SignalWaiter:

    """
    Objects of this class are waiting for named signals on specified object

    Objects of this class are waiting for named signals on specified object,
    puts them in some sort of buffer and returns them one by one with pop
    method waiting for the next one if buffer is empty

    example::

    w = SignalWaiter(obj, _signal_name)
    w.start()

    obj.do_some_stuff_which_results_in_calling_desired_signals()

    # at the point of this comment, obj may already signaled some signals, and
    # if it so, w.pop() will not even wait at all and will immediately return
    # next new signal data

    w.pop()
    w.pop()

    obj.do_some_stuff_which_results_in_calling_desired_signals()

    w.pop()

    w.stop()

    pop() method has a timeout parameter. if timeout occur - ``None`` will be
    returned
    """

    def __init__(self, obj, signal_name, debug=False):
        """
        signal_names same as in :meth:`Signal.connect`
        """

        if not isinstance(obj, Signal):
            raise TypeError("`obj' must by of type Signal")

        self._debug = debug
        self._obj = obj
        self._signal_name = signal_name
        self._signal_received = threading.Event()
        self._buffer = []

        return

    def start(self):

        if self._debug:
            logging.debug(
                "({}) Starting following `{}'".format(self, self._signal_name)
                )

        self._obj.connect(self._signal_name, self._cb)

        return

    def stop(self):

        if self._debug:
            logging.debug(
                "({}) Stopping following `{}'".format(self, self._signal_name)
                )

        self._obj.disconnect(self._cb)

        while len(self._buffer) != 0:
            del self._buffer[0]

        return

    def pop(self, timeout=10):
        """
        timeout meaning is same as for threading.Event.wait() (seconds)

        if timeout occurs, current waiter is stopped automatically and None is
        returned

        if this object internal object has some data, this data is returned in
        form of dict with keys 'event', 'args', 'kwargs'. each such dict is
        representation of call to this class' internal signal listener

        NOTE: be advised: calling this method for not :meth:`start()`ed object
        will result in timeout in any way.
        """
        ret = None
        if self._debug:
            logging.debug("({}) Waiting".format(self))

        timedout = False

        if len(self._buffer) == 0:

            self._signal_received.wait(timeout)

            if len(self._buffer) == 0:
                self.stop()
                timedout = True
                if self._debug:
                    logging.debug(
                        "({}) Timedout".format(
                            self
                            )
                        )

        if timedout:
            ret = None
        else:
            ret = self._buffer.pop(0)
            if self._debug:
                logging.debug(
                    "({}) Popping signal `{}'".format(
                        self,
                        ret
                        )
                    )

        return ret

    def _cb(self, event, *args, **kwargs):
        data = {
            'event': event,
            'args': args,
            'kwargs': kwargs
            }
        self._buffer.append(data)

        if self._debug:
            logging.debug("({}) Received `{}'".format(self, data))

        self._signal_received.set()
        self._signal_received.clear()
        return


class Hub:

    # NOTE: let it stey for history reasons. to not impliment such
    #       functionality again

    def __init__(self):
        raise Exception("Deprecated")
        self._clear(init=True)
        return

    def _clear(self, init=False):
        self.waiters = {}
        return

    def clear(self):
        self._clear()
        return

    def _dispatch(self, *args, **kwargs):

        w = copy.copy(self.waiters)
        w_l = sorted(w.keys())

        for i in w_l:

            threading.Thread(
                target=self._waiter_thread,
                name="`{}' dispatcher to `{}'".format(
                    type(self).__name__,
                    i
                    ),
                args=(w[i], args, kwargs,),
                kwargs=dict()
                ).start()

    def _waiter_thread(self, call, args, kwargs):

        call(*args, **kwargs)

        return

    def set_waiter(self, name, reactor):

        self.waiters[name] = reactor

        return

    def has_waiter(self, name):
        return name in self.waiters

    def get_waiter(self, name):

        ret = None

        if self.has_waiter(name):
            ret = self.waiters[name]

        return ret

    def del_waiter(self, name):

        if name in self.waiters:
            del self.waiters[name]

        return


class CallQueue:

    def __init__(self, target_callable):

        self._target_callable = target_callable
        self._signal_instance = None
        self._signal_name = None
        self._queue = []
        self._call_block = threading.Lock()

        return

    @classmethod
    def new_for_signal(
            cls,
            target_callable,
            signal_instance=None, signal_name=None
            ):

        ret = cls(target_callable)
        ret.set_signal(signal_instance, signal_name)

        signal_instance.connect(signal_name, ret)

        return ret

    def set_signal(self, signal_instance=None, signal_name=None):
        self._signal_instance = signal_instance
        self._signal_name = signal_name
        return

    def set_callable_target(self, target_callable):
        self._target_callable = target_callable
        return

    def copy(self):
        if (not isinstance(self._signal_instance, Signal)
            or self._signal_name is None
            ):
            raise ValueError(
                "`signal_instance' and `signal_name' must be defined"
                )

        if self._queue is None:
            raise Exception("this queue already dumped")

        with self._call_block:

            self._signal_instance.freeze_emition()

            ret = CallQueue.new_for_signal(
                self._target_callable,
                self._signal_instance,
                self._signal_name
                )
            ret._queue = copy.copy(self._queue)

            self._signal_instance.unfreeze_emition()

        return ret

    def dump(self):
        with self._call_block:

            while not len(self._queue) == 0:
                call = self._queue.pop(0)
                logging.debug(
                    "{}, calling {} ({}, {})".format(
                        self,
                        self._target_callable,
                        call['args'],
                        call['kwargs']
                        )
                    )
                _t = threading.Thread(
                    name="thread {} calling {} ({}, {})".format(
                        self,
                        self._target_callable,
                        call['args'],
                        call['kwargs']
                        ),
                    target=self._target_callable,
                    args=call['args'],
                    kwargs=call['kwargs']
                    )
                _t.start()
            self._queue = None

        return

    def __call__(self, *args, **kwargs):

        with self._call_block:

            if self._queue is not None:
                self._queue.append({'args': args, 'kwargs': kwargs})
            else:
                logging.debug(
                    "{}, calling {} ({}, {})".format(
                        self,
                        self._target_callable,
                        args,
                        kwargs
                        )
                    )
                _t = threading.Thread(
                    name="thread {} calling {} ({}, {})".format(
                        self,
                        self._target_callable,
                        args,
                        kwargs
                        ),
                    target=self._target_callable,
                    args=args,
                    kwargs=kwargs
                    )
                _t.start()

        return


class TimeoutForEternity:

    """
    This class is for calling callables, which not support timeout
    """

    @classmethod
    def run(cls, call, args, kwargs, timeout=10, default=None):
        a = cls(call, args, kwargs, timeout, default)
        return a.call()

    def __init__(self, call, args, kwargs, timeout=10, default=None):
        """
        timeout - seconds
        """

        if not timeout > 0:
            raise ValueError("invalid timeout value")

        self._timeout = timeout

        self._call = call
        self._args = args
        self._kwargs = kwargs

        self._normal_exit = False
        self._call_result = default

        self._thread_terminator = threading.Event()
        self._thread_terminator.clear()

        return

    def call(self):
        """
        return: correct_exit?, returned_value
        """

        self._normal_exit = False

        threading.Thread(
            target=self._caller,
            args=self._args,
            kwargs=self._kwargs
            ).start()

        waited = 0.0
        while True:
            if self._normal_exit == True:
                break
            time.sleep(0.2)
            waited += 0.2
            if waited >= self._timeout:
                break

        return self._normal_exit, self._call_result

    def _caller(self, *args, **kwargs):
        self._call_result = self._call(*args, **kwargs)
        self._normal_exit = True
        return


def _add_prefix(signal_names=None, add_prefix=None):

    if not wayround_org.utils.types.struct_check(
            signal_names,
            {'t': list, '.': {'t': str}}
            ):
        raise ValueError("`signal_names' must be None, str or list of str")

    lst = copy.copy(signal_names)

    ret = []

    if add_prefix:
        for i in lst:
            ret.append('{}{}'.format(add_prefix, i))
    else:
        ret = lst

    return ret


class ObjectLock:

    def __init__(self):
        self._on_lock = threading.Event()
        self._on_unlock = threading.Event()
        self._locked = True
        self._locked_lock = threading.RLock()
        self._context_lock = threading.Lock()
        self.unlock()
        return

    def __enter__(self):
        self._context_lock.acquire()
        self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()
        self._context_lock.release()
        return

    def set_locked(self, value):
        if not isinstance(value, bool):
            raise TypeError("`value' must be bool")

        with self._locked_lock:
            prev_value = self.get_locked()
            self._locked = value

            changed = self._locked != prev_value
            if changed:
                if prev_value:
                    self._on_unlock.set()
                    self._on_unlock.clear()
                else:
                    self._on_lock.set()
                    self._on_lock.clear()

        return changed

    def get_locked(self):
        with self._locked_lock:
            ret = self._locked
        return ret

    def get_is_locked(self):
        return self.get_locked()

    def lock(self):
        return self.set_locked(True)

    def unlock(self):
        return self.set_locked(False)

    def acquire(self):
        return self.lock()

    def release(self):
        return self.unlock()

    def wait_lock(self, *args, **kwargs):
        return self._on_lock.wait(*args, **kwargs)

    def wait_unlock(self, *args, **kwargs):
        return self._on_unlock.wait(*args, **kwargs)


class ObjectLocker:

    # TODO: develop persistent locking functional

    def __init__(self, weak_object_mode=True):
        if weak_object_mode:
            self._storage = weakref.WeakValueDictionary()
        else:
            self._storage = {}

        self._storage_lock = threading.Lock()

        return

    def get_lock(self, obj):
        """
        auto-create if not exists
        """
        with self._storage_lock:
            if not obj in self._storage:
                _t = ObjectLock()
                self._storage[obj] = _t
            ret = self._storage[obj]
        return ret

    def get_is_locked(self, obj):
        ret = False
        with self._storage_lock:
            if obj in self._storage:
                lock = self._storage[obj]
                ret = lock.get_locked()
        return ret

    def __getitem__(self, obj):
        return self.get_lock(obj)

    def __in__(self, obj):
        with self._storage_lock:
            ret = obj in self._storage
        return ret
