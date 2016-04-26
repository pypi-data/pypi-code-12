"""Test suites for the ICoroutine processor implementation."""

import concurrent.futures

import iface
import pytest

from asyncdef.interfaces.engine import icoroutine

from . import coroutine


@pytest.fixture(scope='function')
def processor():
    """Get a test processor."""
    return coroutine.Coroutine()


class AwaitableFuture(concurrent.futures.Future):

    """An awaitable version of the standard lib Future."""

    def __await__(self):
        """Return self until resolved."""
        while self._state != 'FINISHED':

            yield self

        return self.result()


@pytest.fixture(scope='function')
def future():
    """Get a new future object."""
    return AwaitableFuture()


def test_coro_implements_interface(processor):
    """Check if the implementation implements the interface."""
    assert iface.isinstance(processor, icoroutine.ICoroutine)


def test_coro_executes_coroutines(processor):
    """Check if the processor exhausts coroutines."""
    state = {"executed": False}

    async def flip_bit():
        state['executed'] = True

    processor.add(flip_bit())
    processor()
    assert state['executed'] is True


def test_coro_waits_for_future(processor, future):
    """Check if the processor waits for futures."""
    state = {"toggled": False}
    sentinel = object()

    async def wait_and_toggle(f):
        result = await f
        assert result is sentinel
        state['toggled'] = True

    processor.add(wait_and_toggle(future))
    for _ in range(10):

        processor()
        assert state['toggled'] is False

    future.set_result(sentinel)
    processor()
    assert state['toggled'] is True
