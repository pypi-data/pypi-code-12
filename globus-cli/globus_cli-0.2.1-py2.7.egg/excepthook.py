"""
Setup a custom except hook which formats exceptions that are uncaught.
In "DEBUGMODE", we'll just use the typical sys.excepthook behavior and print a
stacktrace. It's really for debugging problems with the CLI itself, but it
might also come in handy if we have issues with the way that we're trying to
format an exception.
Define an except hook per exception type that we want to treat specially,
generally types of SDK errors, and dispatch onto tht set of hooks.
"""
from __future__ import print_function

import sys
import os
import errno

from globus_sdk import exc


_prefix = 'Globus CLI Error:'
_prefix_len = len(_prefix)


def _errmsg(msg):
    print('{} {}'.format(_prefix, msg), file=sys.stderr)


def _format_error_field(name, val, multiline=False):
    name = name + ':'
    if not multiline or '\n' not in val:
        return '{} {}'.format(name.ljust(_prefix_len), val)
    else:
        spacer = '\n' + ' '*(_prefix_len + 1)
        return '{}{}{}'.format(name, spacer, spacer.join(val.split('\n')))


def pagination_overrun_hook():
    _errmsg(('Some kind of paging error happened. '
             'Likely an issue with the CLI or Globus SDK.'))


def transferapi_hook(exception):
    _errmsg(('A Transfer API Error Occurred.\n{}\n{}\n{}\n{}').format(
            _format_error_field('HTTP status', exception.http_status),
            _format_error_field('request_id', exception.request_id),
            _format_error_field('code', exception.code),
            _format_error_field('message', exception.message, multiline=True)))


def globusapi_hook(exception):
    _errmsg(('A Globus API Error Occurred.\n'
             '{}\n{}\n{}').format(
        _format_error_field('HTTP status', exception.http_status),
        _format_error_field('code', exception.code),
        _format_error_field('message', exception.message, multiline=True)))


def custom_except_hook(exception_type, exception, traceback,
                       _bound_excepthook=sys.excepthook):
    """
    A custom excepthook to present python errors produced by the CLI.
    We don't want to show end users big scary stacktraces if they aren't python
    programmers, so slim it down to some basic info. We keep a "DEBUGMODE" env
    variable kicking around to let us turn on stacktraces if we ever need them.

    Additionally, does global suppression of EPIPE errors, which often occur
    when a python command is piped to a consumer like `head` which closes its
    input stream before python has sent all of its output.
    DANGER: There is a (small) risk that this will bite us if there are EPIPE
    errors produced within the Globus SDK. We should keep an eye on this
    possibility, as it may demand more sophisticated handling of EPIPE.
    Possible TODO item to reduce this risk: inspect the exception and only hide
    EPIPE if it comes from within the globus_cli package.

    Abuses bind at definition time to capture the "real" excepthook.
    """
    # handle a broken pipe by doing nothing
    # this is normal, and often shows up in piped commands when the
    # consumer closes before the producer
    if exception_type is IOError and exception.errno is errno.EPIPE:
        return

    # check if we're in debug mode, and run the real excepthook if we are
    if os.environ.get('GLOBUS_CLI_DEBUGMODE', None) is not None:
        _bound_excepthook(exception_type, exception, traceback)

    # we're not in debug mode, do custom handling
    else:
        if exception_type is exc.PaginationOverrunError:
            pagination_overrun_hook()
        elif exception_type is exc.TransferAPIError:
            transferapi_hook(exception)
        elif exception_type is exc.GlobusAPIError:
            globusapi_hook(exception)
        else:
            print('{}: {}'.format(exception_type.__name__, exception))


def set_excepthook():
    sys.excepthook = custom_except_hook
