"""IProcessor extension that manages coroutine objects."""

import types
import typing

import iface

from . import iprocessor


class ICoroutine(iprocessor.IProcessor):

    """A processor that manages coroutine execution."""

    @iface.method
    def add(self, coro: types.CoroutineType) -> typing.Any:
        """Add a coroutine to the engine for execution.

        Args:
            coro (types.CoroutineType): A coroutine object.

        Returns:
            typing.Any: Some opaque identifier that represents the scheduled
                coroutine within the engine.
        """
        raise NotImplementedError()

    @iface.method
    def cancel(
            self,
            identifier: typing.Any,
            exc_type: typing.Optional[type]=None,
    ) -> bool:
        """Cancel an active coroutine and remove it from the schedule.

        Args:
            identifier (typing.Any): The identifier returned from add.
            exc_type (typing.Optional[type]): The exception type to throw into
                the coroutine on cancel. No exception is thrown if nothing is
                given. Instead the coroutine is no longer processed.

        Returns:
            bool: True if the coroutine is cancelled. False if the identifier
                is invalid or if the coroutine is complete.
        """
        raise NotImplementedError()
