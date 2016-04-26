"""ISelector processor implementation."""

import logging
import selectors
import typing

from asyncdef.interfaces.engine import iselector

from . import base


class Selector(base.Processor):

    """Implementation of the ISelector processor interface.

    This implementation uses the standard library selectors module to manage
    polling for IO events.
    """

    def __init__(
            self,
            selector: selectors.BaseSelector=None,
            timeout=None,
            exc_handler: typing.Callable[[], None]=None,
            logger: logging.Logger=None,
    ):
        """Initialize the processor with an optional selector."""
        super().__init__(exc_handler, logger)
        self._selector = selector or selectors.DefaultSelector()
        self._timeout = timeout

    def __call__(self):
        """Execute the processor."""
        self._handle_events()

    def _handle_event(self, key, event_mask):
        """Handle a single event."""
        reader, writer, fd = key.data
        if event_mask & selectors.EVENT_READ and reader:

            reader(fd)

        if event_mask & selectors.EVENT_WRITE and writer:

            writer(fd)

    def _handle_events(self):
        """Poll the selector for IO events and dispatch them."""
        for key, event_mask in self._selector.select(self._timeout):

            self._handle_event(key, event_mask)

    def add_reader(
            self,
            fd: iselector.IFileLike,
            callback: typing.Callable[[iselector.IFileLike], typing.Any],
    ) -> None:
        """Add a file descriptor to the processor and wait for READ.

        Args:
            fd (iselector.IFileLike): Any obect that exposes a 'fileno' method
                that returns a valid file descriptor integer.
            callback (typing.Callable[[iselector.IFileLike], typing.Any]): A
                function that consumes the IFileLike object whenever the READ
                event is fired.
        """
        try:

            key = self._selector.get_key(fd)

        except KeyError:

            key = None

        if key is None:  # FD not already registered.

            self._selector.register(
                fd,
                selectors.EVENT_READ,
                (callback, None, fd),
            )
            return None

        _, writer, fd = key.data
        self._selector.modify(
            fd,
            selectors.EVENT_READ | key.events,
            (callback, writer, fd),
        )

    def remove_reader(self, fd: iselector.IFileLike) -> bool:
        """Remove a file descriptor waiting for READ from the processor.

        Args:
            fd (iselector.IFileLike): Any obect that exposes a 'fileno' method
                that returns a valid file descriptor integer.

        Returns:
            bool: True if the reader was removed. False if it was not in the
                processor.
        """
        try:

            key = self._selector.get_key(fd)

        except KeyError:

            return False

        _, writer, fd = key.data
        new_mask = key.events & ~selectors.EVENT_READ
        if not new_mask:

            self._selector.unregister(fd)
            return True

        self._selector.modify(
            fd,
            new_mask,
            (None, writer, fd)
        )
        return True

    def add_writer(
            self,
            fd: iselector.IFileLike,
            callback: typing.Callable[[iselector.IFileLike], typing.Any],
    ) -> None:
        """Add a file descriptor to the processor and wait for WRITE.

        Args:
            fd (iselector.IFileLike): Any obect that exposes a 'fileno' method
                that returns a valid file descriptor integer.
            callback (typing.Callable[[iselector.IFileLike], typing.Any]): A
                function that consumes the IFileLike object whenever the WRITE
                event is fired.
        """
        try:

            key = self._selector.get_key(fd)

        except KeyError:

            key = None

        if key is None:  # FD not already registered.

            self._selector.register(
                fd,
                selectors.EVENT_WRITE,
                (None, callback, fd),
            )
            return True

        reader, _, fd = key.data
        self._selector.modify(
            fd,
            selectors.EVENT_WRITE | key.events,
            (reader, callback, fd),
        )

    def remove_writer(self, fd: iselector.IFileLike) -> bool:
        """Remove a file descriptor waiting for WRITE from the processor.

        Args:
            fd (iselector.IFileLike): Any obect that exposes a 'fileno' method
                that returns a valid file descriptor integer.

        Returns:
            bool: True if the reader was removed. False if it was not in the
                processor.
        """
        try:

            key = self._selector.get_key(fd)

        except KeyError:

            return False

        reader, _, fd = key.data
        new_mask = key.events & ~selectors.EVENT_WRITE
        if not new_mask:

            self._selector.unregister(fd)
            return True

        self._selector.modify(
            fd,
            new_mask,
            (reader, None, fd)
        )
        return True
