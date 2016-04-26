"""IProcessor extension that manages time based events."""

import typing

import iface

from . import iprocessor


class ITime(iprocessor.IProcessor):

    """A processor that handles time based events."""

    @iface.property
    def time(self) -> typing.Union[int, float]:
        """Get the current processor time.

        The time must always be returned as a numeric value that represents
        seconds.
        """
        raise NotImplementedError()

    @iface.method
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
        raise NotImplementedError()

    @iface.method
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
        raise NotImplementedError()

    @iface.method
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
        raise NotImplementedError()

    @iface.method
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
        raise NotImplementedError()

    @iface.method
    def cancel(self, identifier: typing.Any) -> bool:
        """Cancel a deferred function call.

        Args:
            identifier (typing.Any): The identifier returned from a call
                to defer or defer_for.

        Returns:
            bool: True if the call is cancelled. False if the identifier is
                invalid or if the deferred call is already executed.
        """
        raise NotImplementedError()

    @iface.method
    def pending(self, identifier: typing.Any) -> bool:
        """Get the pending status of a deferred function call.

        Args:
            identifier (typing.Any): The identifier returned from a call
                to defer or defer_for.

        Returns:
            bool: True if the call is pending. False if the identifier is
                invalid or if the deferred call is executed.
        """
        raise NotImplementedError()
