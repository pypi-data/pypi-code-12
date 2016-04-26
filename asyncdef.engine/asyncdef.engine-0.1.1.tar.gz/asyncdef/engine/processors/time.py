"""ITime processor implementation."""

import logging
import time
import typing

from . import base


class DeferredCall:

    """A function call that has been deferred for some amount of time."""

    __slots__ = ('func', 'when')

    def __init__(self, func, when):
        """Initialize with a callable and a time."""
        self.func = func
        self.when = when


class Time(base.Processor):

    """An implementation of the ITime processor interface."""

    def __init__(
            self,
            timer: typing.Callable[[], typing.Union[int, float]]=None,
            exc_handler: typing.Callable[[], None]=None,
            logger: logging.Logger=None,
    ):
        """Inititalize the timer and callback queues."""
        super().__init__(exc_handler, logger)
        self._deferred_calls = {}
        self._timer = timer or time.monotonic

    def __call__(self) -> None:
        """Execute the processor."""
        self._handle_deferred_calls()

    def _handle_deferred_calls(self):
        """Process the deferred call queue."""
        plucks = []
        for key, deferred_call in self._deferred_calls.items():

            if deferred_call.when <= self.time:

                plucks.append(key)
                try:

                    deferred_call.func()

                except Exception:

                    self.handle_exception()

        for pluck in plucks:

            self._deferred_calls.pop(pluck, None)

    @property
    def time(self) -> typing.Union[int, float]:
        """Get the current processor time.

        The time must always be returned as a numeric value that represents
        second values.
        """
        return self._timer()

    def defer(
            self,
            func: typing.Callable[[], typing.Any],
            until: typing.Union[int, float]=-1,
    ) -> typing.Any:
        """Defer the execution of a function until some clock value.

        Args:
            func (typing.Callable[[], typing.Any]): A callable that accepts no
                arguments. All return values are ignored.
            until (typing.Union[int, float]): A numeric value that represents
                the clock time when the callback becomes available for
                execution. Values that are less than the current time result in
                the function being called at the next opportunity.

        Returns:
            typing.Any: An opaque identifier that represents the callback
                uniquely within the processor. This identifier is used to
                modify the callback scheduling.

        Note:
            The time given should not be considered absolute. It represents
            the time when the callback becomes available to execute. It may
            be much later than the given time value when the function actually
            executes depending on the implementation.
        """
        deferred_call = DeferredCall(func, until)
        key = object()
        self._deferred_calls[key] = deferred_call
        return key

    def defer_for(
            self,
            wait: typing.Union[int, float],
            func: typing.Callable[[], typing.Any],
    ) -> typing.Any:
        """Defer the execution of a function for some number of seconds.

        Args:
            wait (typing.Union[int, float]): A numeric value that represents
                the number of seconds that must pass before the callback
                becomes available for execution. All given values must be
                positive.
            func (typing.Callable[[], typing.Any]): A callable that accepts no
                arguments. All return values are ignored.

        Returns:
            typing.Any: An opaque identifier that represents the callback
                uniquely within the processor. This identifier is used to
                modify the callback scheduling.
        """
        return self.defer(func, self.time + wait)

    def delay(
            self,
            identifier: typing.Any,
            until: typing.Union[int, float]=-1,
    ) -> bool:
        """Delay a deferred function until the given time.

        Args:
            identifier (typing.Any): The identifier returned from a call
                to defer or defer_for.
            until (typing.Union[int, float]): A numeric value that represents
                the clock time when the callback becomes available for
                execution. Values that are less than the current time result in
                the function being called at the next opportunity.

        Returns:
            bool: True if the call is delayed. False if the identifier is
                invalid or if the deferred call is already executed.
        """
        deferred_call = self._deferred_calls.get(identifier, None)
        if not deferred_call:

            return False

        deferred_call.when = until
        return True

    def delay_for(
            self,
            wait: typing.Union[int, float],
            identifier: typing.Any,
    ) -> bool:
        """Defer the execution of a function for some number of seconds.

        Args:
            wait (typing.Union[int, float]): A numeric value that represents
                the number of seconds that must pass before the callback
                becomes available for execution. All given values must be
                positive.
            identifier (typing.Any): The identifier returned from a call
                to defer or defer_for.

        Returns:
            bool: True if the call is delayed. False if the identifier is
                invalid or if the deferred call is already executed.
        """
        deferred_call = self._deferred_calls.get(identifier, None)
        if not deferred_call:

            return False

        deferred_call.when += wait
        return True

    def cancel(self, identifier: typing.Any) -> bool:
        """Cancel a deferred function call.

        Args:
            identifier (typing.Any): The identifier returned from a call
                to defer or defer_for.

        Returns:
            bool: True if the call is cancelled. False if the identifier is
                invalid or if the deferred call is already executed.
        """
        deferred_call = self._deferred_calls.pop(identifier, None)
        return deferred_call is not None

    def pending(self, identifier: typing.Any) -> bool:
        """Get the pending status of a deferred function call.

        Args:
            identifier (typing.Any): The identifier returned from a call
                to defer or defer_for.

        Returns:
            bool: True if the call is pending. False if the identifier is
                invalid or if the deferred call is executed.
        """
        return identifier in self._deferred_calls
