
"""define some wrapper to wrapt some method in tornado http server
"""

import logging
from tingyun.logistics.basic_wrapper import wrap_function_wrapper
from tingyun.armoury.ammunition.tornado_4.utils import finish_tracker

console = logging.getLogger(__name__)


def trace_tracker_export(wrapped, instance, args, kwargs):
    """
    """
    # the request maybe exist two situations in httpserver delegate
    request = instance.delegate.request if instance.delegate else instance.request

    if not request:
        console.warning("No request got in _ServerRequestAdapter object. this should not be happen. if this continue."
                        " please report us.")
        return wrapped(*args, **kwargs)

    tracker = getattr(request, "_self_tracker", None)
    if not tracker:
        return wrapped(*args, **kwargs)

    try:
        wrapped(*args, **kwargs)
    finally:
        setattr(tracker, "_can_finalize", True)
        finish_tracker(tracker)


def detect_tracker_export(module):
    """detect the export of the tracker.
    :param module: tornado httpserver
    :return:
    """
    wrap_function_wrapper(module, "_ServerRequestAdapter.on_connection_close", trace_tracker_export)
    wrap_function_wrapper(module, "_ServerRequestAdapter.finish", trace_tracker_export)
