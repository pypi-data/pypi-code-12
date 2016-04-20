# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import (
    absolute_import, unicode_literals, division, print_function
)

import sys
from functools import wraps

from tornado import gen


def set_exc_info(future, exc_info):
    if hasattr(future, 'set_exception_info'):
        # Concurrent futures
        future.set_exception_info(*exc_info[1:])
    else:
        future.set_exc_info(exc_info)


def transform(future, f):
    """Transforms the result of a future.

    Returns a new future that resolves to ``f(future.result())`` when the
    future succeeds, or an exception if the future failed, or if ``f`` failed.
    """
    answer = future.__class__()

    @fail_to(answer)
    def on_done(future):
        result = future.result()
        result = f(result)
        answer.set_result(result)

    future.add_done_callback(on_done)
    return answer


def fail_to(future):
    """A decorator for function callbacks to catch uncaught non-async
    exceptions and forward them to the given future.

    The primary use for this is to catch exceptions in async callbacks and
    propagate them to futures. For example, consider,

    .. code-block:: python

        answer = Future()

        def on_done(future):
            foo = bar()
            answer.set_result(foo)

        some_async_operation().add_done_callback(on_done)

    If ``bar()`` fails, ``answer`` will never get filled with an exception or
    a result. Now if we change ``on_done`` to,

    .. code-block:: python

        @fail_to(answer)
        def on_done(future):
            foo = bar()
            answer.set_result(foo)

    Uncaught exceptions in ``on_done`` will be caught and propagated to
    ``answer``. Note that ``on_done`` will return None if an exception was
    caught.

    :param answer:
        Future to which the result will be written.
    """
    assert gen.is_future(future), 'you forgot to pass a future'

    def decorator(f):

        @wraps(f)
        def new_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                set_exc_info(future, sys.exc_info())

        return new_f

    return decorator


def maybe_async(f, *args, **kwargs):
    """Calls a function that might be asynchronous with the given arguments.

    Returns a Future that contains the result of calling the function or the
    failure.

    .. code-block:: python

        maybe_async(f, 1, 2).add_done_callback(on_done)

    This may be used when a function may or may not be asynchronous and both
    cases need to be handled in the same way with respect to failures.
    """
    answer = gen.Future()

    try:
        result = f(*args, **kwargs)
    except Exception:
        answer.set_exc_info(sys.exc_info())
    else:
        if gen.is_future(result):
            _copy_future(answer, result)
        else:
            answer.set_result(result)
    return answer


def _copy_future(dest, src):
    """Sets up the output of ``src`` to be copied into ``dest``."""

    def on_done(future):
        if future.exception():
            dest.set_exc_info(src.exc_info())
        else:
            dest.set_result(src.result())

    src.add_done_callback(on_done)
