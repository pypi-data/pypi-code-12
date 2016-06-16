
"""define a detector for detect concurrent module
"""

import logging
from tingyun.logistics.object_name import callable_name
from tingyun.logistics.basic_wrapper import wrap_function_wrapper
from tingyun.armoury.ammunition.tornado_4.utils import create_tracker_aware_fxn, obtain_current_tracker

console = logging.getLogger(__name__)
fxn_cache = []


def trace_add_done_callback(wrapped, instance, args, kwargs):
    """
    """
    def _fxn_arg_extractor(fn, *args, **kwargs):
        return fn

    fxn = _fxn_arg_extractor(*args, **kwargs)
    should_trace = callable_name(fxn) not in fxn_cache
    tracker_aware_fxn = create_tracker_aware_fxn(fxn, should_trace=should_trace)
    if should_trace:
        fxn_cache.append(callable_name(fxn))

    # If tracker_aware_fxn is None then it is already wrapped, or the fxn is None.
    if tracker_aware_fxn is None:
        return wrapped(*args, **kwargs)

    tracker = obtain_current_tracker()
    tracker_aware_fxn._self_tracker = tracker

    # We replace the function we call in the callback with the tracker aware version of the function.
    if len(args) > 0:
        args = list(args)
        args[0] = tracker_aware_fxn
    else:
        kwargs['fn'] = tracker_aware_fxn

    return wrapped(*args, **kwargs)


def detect_concurrent(module):
    """
    """
    wrap_function_wrapper(module, 'Future.add_done_callback', trace_add_done_callback)
