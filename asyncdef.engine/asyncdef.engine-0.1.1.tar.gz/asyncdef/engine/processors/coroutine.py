"""ICoroutine implementation."""

import enum
import functools
import logging
import types
import typing

from . import base


class CoroutineStatus(enum.Enum):

    """Possible statuses for a coroutine object."""

    ACTIVE = 0
    PAUSED = 1
    DEPLETED = 2
    FAILED = 3
    CANCELLED = 4


class CoroutineWrapper:

    """Coroutine wrapper used to manage state."""

    __slots__ = (
        'coro',
        'throw_value',
        'state',
        'paused_by',
        'key',
    )

    def __init__(self, coro: types.CoroutineType, key: typing.Any):
        """Seed the wrapper with a coroutine object.

        Args:
            coro (types.CoroutineType): The coroutine object to wrap.
            key (typing.Any): A lookup key.
        """
        self.coro = coro
        self.throw_value = None
        self.state = CoroutineStatus.ACTIVE
        self.paused_by = None
        self.key = key

    def send(self, *args, **kwargs):
        """Proxy the coroutine send method."""
        return self.coro.send(*args, **kwargs)

    def throw(self, *args, **kwargs):
        """Proxy the coroutine throw method."""
        return self.coro.throw(*args, **kwargs)


class Coroutine(base.Processor):

    """A processor that manages coroutine execution."""

    def __init__(
            self,
            exc_handler: typing.Callable[[], None]=None,
            logger: logging.Logger=None,
    ):
        """Initialize the coroutine storage."""
        super().__init__(exc_handler, logger)
        self._coroutines = {}

    def __call__(self):
        """Execute the processor."""
        self._handle_coroutines()

    def _handle_coroutine(self, coro: CoroutineWrapper) -> bool:
        """Process a coroutine.

        Args:
            coro (CoroutineWrapper): The coroutine wrapper to manage.

        Returns:
            bool: Whether or not the coroutine is complete.
        """
        try:

            if coro.throw_value:

                throw_value, coro.throw_value = coro.throw_value, None
                value = coro.throw(*throw_value)

            else:

                value = coro.send(None)

        except StopIteration:

            coro.state = CoroutineStatus.DEPLETED
            return True

        except Exception:

            coro.state = CoroutineStatus.FAILED
            return True

        if (
                hasattr(value, 'add_done_callback') and
                callable(value.add_done_callback)
        ):

            # Assuming a reasonable implementation of concurrent.futures.
            coro.state = CoroutineStatus.PAUSED
            coro.paused_by = value
            value.add_done_callback(
                functools.partial(self._unpause_from_future, coro)
            )
            return False

        coro.throw_value = (
            RuntimeError('Invalid yield value {!r}'.format(value)),
        )
        return False

    def _handle_coroutines(self):
        """Process coroutines in the queue."""
        plucks = []
        for coro in self._coroutines.values():

            if coro.state is not CoroutineStatus.PAUSED:

                pluck = self._handle_coroutine(coro)
                if pluck:

                    plucks.append(coro)

        for coro in plucks:

            self._coroutines.pop(coro.key, None)

    def _unpause_from_future(self, coro, future):
        """Reactivate a coro that was waiting on a future."""
        coro.state = CoroutineStatus.ACTIVE
        coro.paused_by = None
        problem = future.exception()
        if problem:

            coro.throw_value = (problem,)
            return None

    def add(self, coro: types.CoroutineType) -> typing.Any:
        """Add a coroutine to the engine for execution.

        Args:
            coro (types.CoroutineType): A coroutine object.

        Returns:
            typing.Any: Some opaque identifier that represents the scheduled
                coroutine within the engine.
        """
        key = object()
        self._coroutines[key] = CoroutineWrapper(coro, key)
        return key

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
        coro = self._coroutines.get(identifier, None)
        if not coro:

            return False

        coro.state = CoroutineStatus.CANCELLED
        coro.throw_value = (exc_type(),)
        return True
