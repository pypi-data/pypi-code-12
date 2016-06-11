from __future__ import (
    print_function
)
from functools import wraps
import os

from immunio.context import get_context
from immunio.logger import log


# Set plugin name so it can be enabled and disabled.
NAME = "file_io"


def add_hooks(run_hook, get_agent_func=None, timer=None):
    """
    Add any OS hooks.
    """
    hook_os_open(run_hook)
    hook_builtin_open(run_hook)


def hook_os_open(run_hook):
    """
    Add our hook into os.open
    """
    orig_os_open = os.open

    # Replace the original 'os.open'
    @wraps(orig_os_open)
    def our_os_open(*args, **kwargs):
        log.debug("os.open(%(args)s, %(kwargs)s)", {
            "args": args,
            "kwargs": kwargs,
            })
        # Send hook
        _, loose_context, stack, _ = get_context()
        run_hook("file_io", {
            "method": "os.open",
            "parameters": args,
            "information": kwargs,
            "stack": stack,
            "context_key": loose_context,
            "cwd": os.getcwd()
        })
        return orig_os_open(*args, **kwargs)

    # Replace original with our version
    os.open = our_os_open


def hook_builtin_open(run_hook):
    """
    Add our hook into open.
    """
    import __builtin__

    orig_open = __builtin__.open

    # Replace the original 'open'
    @wraps(orig_open)
    def our_open(*args, **kwargs):
        log.debug("open(%(args)s, %(kwargs)s)", {
            "args": args,
            "kwargs": kwargs,
            })
        # Send hook
        _, loose_context, stack, _ = get_context()
        run_hook("file_io", {
            "method": "open",
            "parameters": args,
            "information": kwargs,
            "stack": stack,
            "context_key": loose_context,
            "cwd": os.getcwd(),
        })
        return orig_open(*args, **kwargs)

    # Replace original with our version
    __builtin__.open = our_open
