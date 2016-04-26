"""Test suite for the IEngine implementation."""

import iface
from asyncdef.interfaces.engine import iengine

from . import core


def test_core_is_implementation():
    """Check if Engine is an IEngine."""
    assert iface.isinstance(
        core.Engine(None, None, None),
        iengine.IEngine
    )


def test_core_stops():
    """Check if the core stops when stop is called."""
    state = {"count": 0}

    def increment():
        """Bump the test value."""
        state['count'] += 1

    def stop():
        """Stop the engine."""
        engine.stop()

    engine = core.Engine(increment, stop)
    engine.start()
    assert state['count'] == 1


def test_core_steps():
    """Check if the core can be pushed with `next`."""
    state = {"count": 0}

    def increment():
        """Bump the test value."""
        state['count'] += 1

    engine = core.Engine(increment)
    next(engine)
    assert state['count'] == 1
    next(engine)
    assert state['count'] == 2
