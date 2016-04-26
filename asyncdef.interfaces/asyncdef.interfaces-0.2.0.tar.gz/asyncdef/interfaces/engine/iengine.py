"""Implementable interfaces for the engine core."""

import typing

import iface

from . import iprocessor


class IEngine(iface.Iface):

    """A basic, controllable engine.

    The core engine interface allows for very simple start and stop control.
    Additionally, it must be an iterator. Each call of `next(engine)` pushes
    the internal loop by one iteration.
    """

    @iface.attribute
    def processors(self) -> typing.Iterable[iprocessor.IProcessor]:
        """Get an iterable of all processors attached to the engine."""
        raise NotImplementedError()

    @iface.attribute
    def running(self) -> bool:
        """Get whether the engine is currently running or not."""
        raise NotImplementedError()

    @iface.method
    def start(self) -> None:
        """Start the engine and run it until stopped."""
        raise NotImplementedError()

    @iface.method
    def stop(self) -> None:
        """Stop the engine from executing."""
        raise NotImplementedError()

    @iface.method
    def __next__(self) -> None:
        """Push the engine one step."""
        raise NotImplementedError()
