from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from collections import namedtuple
import sys
import time

from immunio.logger import log


# Performance measurement changes in Python3.3 - select the best timing function
if hasattr(time, "perf_counter"):
    perf_time = time.perf_counter
else:
    if sys.platform == "win32":
        # On Windows, the best timer is time.clock()
        perf_time = time.clock
    else:
        # On most other platforms the best timer is time.time()
        perf_time = time.time


# State store between a timer context manager starting and completing.
TimerState = namedtuple("TimerState",
                        ["report_name", "exclude", "exclude_times"])


class TimerContext(object):
    """
    Context manager for timing the duration of a `with` block. Measures
    the duration of the block, then calls the `complete_callback` with a
    single `duration` argument.

    Note that we aren't using a `contextlib.contextmanager` here. It does
    not behave well when the code within the timer block raises
    `StopException` errors. They interfere somehow with the `contextmanager`
    use of generator syntax. This explicit __enter__ and __exit__ syntax is
    a bit more verbose but works well.
    """
    def __init__(self, complete_callback):
        self.complete_callback = complete_callback
        self.start_time = None

    def __enter__(self):
        """
        Start the timer.
        """
        self.start_time = perf_time()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Compute the duration and call the callback. If there were any
        exceptions still grab the time and allow the exception to propogate.
        """
        duration = perf_time() - self.start_time
        self.complete_callback(duration)


class DummyTimer(object):
    """
    Dummy "no-op" timer
    """
    def __call__(self, report_name=None, exclude=False):
        return TimerContext(self.timer_block_complete)

    def timer_block_complete(self, duration):
        """
        Do Nothing.
        """


class Timer(object):
    def __init__(self, report_callback=None):
        self.report_callback = report_callback
        self.timer_stack = []

    def set_report_callback(self, report_callback):
        self.report_callback = report_callback

    def __call__(self, report_name=None, exclude=False):
        """
        Called to create a new Context Manager around a block of code.

        Use is like:

        with timer("my name"):
            code_to_time()
            goes_here()
        """
        # We can only exclude if another timer is already in progress
        if exclude and not self.timer_stack:
            raise Exception("Can't exclude time with no timer in progress")

        self.timer_stack.append(TimerState(report_name, exclude, list()))

        # Return the actual Context Manager to time the block.
        return TimerContext(self._timer_block_complete)

    def _timer_block_complete(self, duration):
        """
        Collects the durations after each context block completes.
        """
        state = self.timer_stack.pop()
        # Remove any excluded times from this duration
        duration -= sum(state.exclude_times)
        # If this is an excluded time, add info to the parent
        if state.exclude:
            # This duration should be excluded from the containing duration
            parent = self.timer_stack[-1]
            if parent.exclude:
                # Two timers with `exclude=True` shouldn't be nested since
                # it's not clear if the second timer should reduce or expand
                # the exluded time.
                #
                # We have seen a few cases where this happens however which
                # we haven't been able to reproduce. Instead of raising an
                # exception in this cases, we just log for now.
                #
                # If an excluded timer is within another excluded timer,
                # the internal one is ignored, since its duration is already
                # excluded by the parent.
                log.debug("Excluding time `%(report_name)s` within another"
                          "exclude. Stack: %(stack)s", {
                    "report_name": state.report_name,
                    "stack": self.timer_stack,
                })
                return
            parent.exclude_times.append(duration)
        if state.report_name and self.report_callback:
            # Internally we track everything as seconds, but the reported
            # duration must be in milliseconds. We truncate the resolution
            # at the microsecond level then convert to milliseconds.
            duration_ms = int(duration * 1000000) / 1000
            self.report_callback(state.report_name, duration_ms)
