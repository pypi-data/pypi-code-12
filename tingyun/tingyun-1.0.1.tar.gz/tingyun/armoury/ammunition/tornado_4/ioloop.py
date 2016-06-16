
"""define a detector for tornado ioloop
"""

import sys
import logging
from tingyun.armoury.ammunition.tornado_4.utils import finish_tracker, record_exception, obtain_current_tracker
from tingyun.armoury.ammunition.tornado_4.utils import current_thread_id, TrackerTransferContext
from tingyun.logistics.basic_wrapper import wrap_function_wrapper

console = logging.getLogger(__name__)


def trace_run_callback(wrapped, instance, args, kwargs):
    """
    """
    def _get_actually_callback(callback, *args, **kwargs):
        try:
            return callback.func
        except AttributeError:
            return None

    callback = _get_actually_callback(*args, **kwargs)
    tracker = getattr(callback, '_self_tracker', None)
    ret = wrapped(*args, **kwargs)

    if tracker:
        tracker._ref_count -= 1
        finish_tracker(tracker)

    return ret


def trace_handle_callback_exception(wrapped, instance, args, kwargs):
    """
    """
    record_exception(sys.exc_info())

    return wrapped(*args, **kwargs)


def _increment_ref_count(callback, wrapped, instance, args, kwargs):
    tracker = obtain_current_tracker()

    if hasattr(callback, '_self_tracker'):

        if callback._self_tracker is not None:
            if current_thread_id() != callback._self_tracker.thread_id:
                # Callback being added not in the main thread; ignore.

                # Since we are not incrementing the counter for this callback,
                # we need to remove the tracker from the callback, so it
                # doesn't get decremented either.
                callback._self_tracker = None
                return wrapped(*args, **kwargs)

        if tracker is not callback._self_tracker:
            console.warning("Attempt to add callback to ioloop with different tracer attached than in the cache."
                            "if this continue, Please report to us.")
            callback._self_tracker = None
            return wrapped(*args, **kwargs)

    if tracker is None:
        return wrapped(*args, **kwargs)

    tracker._ref_count += 1

    return wrapped(*args, **kwargs)


def trace_add_callback(wrapped, instance, args, kwargs):
    """
    """
    def _get_actually_callback(callback, *args, **kwargs):
        return callback

    callback = _get_actually_callback(*args, **kwargs)
    return _increment_ref_count(callback, wrapped, instance, args, kwargs)


def trace_call_at(wrapped, instance, args, kwargs):
    """
    """
    with TrackerTransferContext(None):
        return wrapped(*args, **kwargs)


def trace_add_handler(wrapped, instance, args, kwargs):
    """
    """
    with TrackerTransferContext(None):
        return wrapped(*args, **kwargs)


def detect_ioloop(module):
    """
    :param module:
    :return:
    """
    wrap_function_wrapper(module, 'IOLoop._run_callback', trace_run_callback)
    wrap_function_wrapper(module, 'IOLoop.handle_callback_exception', trace_handle_callback_exception)
    wrap_function_wrapper(module, 'PollIOLoop.add_callback', trace_add_callback)
    wrap_function_wrapper(module, 'PollIOLoop.call_at', trace_call_at)
    wrap_function_wrapper(module, 'PollIOLoop.add_handler', trace_add_handler)
