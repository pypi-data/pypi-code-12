"""Test suites for the ITime processor implementation."""

import time as stdtime

import iface
import pytest

from asyncdef.interfaces.engine import itime

from . import time


@pytest.fixture(scope='function')
def processor():
    """Get a test processor."""
    return time.Time()


def test_time_implements_interface(processor):
    """Check if the implementation implements the interface."""
    iattrs = set(itime.ITime.__abstractmethods__)
    attrs = set(dir(processor))
    print(sorted(iattrs))
    print(sorted(iattrs.intersection(attrs)))
    assert iface.isinstance(processor, itime.ITime)


def test_time_defer_identifier(processor):
    """Check if the defer method returns an identifier."""
    assert processor.defer(lambda: None)


def test_time_pending(processor):
    """Check if pending is True for valid deferreds."""
    ident = processor.defer(lambda: None)
    assert processor.pending(ident)
    assert not processor.pending(None)


def test_time_cancel(processor):
    """Check if cancel removes the deferred."""
    ident = processor.defer(lambda: None)
    assert processor.pending(ident)
    assert processor.cancel(ident)
    assert not processor.cancel(ident)
    assert not processor.pending(ident)


def test_time_increases(processor):
    """Check that subsequent calls to time give new values."""
    t1 = processor.time
    stdtime.sleep(.00001)
    t2 = processor.time
    assert t2 > t1


def test_time_executes(processor):
    """Check that deferreds fire after the timeout."""
    now = processor.time
    expected = now + .1
    state = {"complete": False}

    def check():
        """Check the test value."""
        state['complete'] = True
        assert processor.time >= expected

    processor.defer_for(.1, check)
    while not state['complete']:

        processor()


def test_time_delay(processor):
    """Check that delaying a deferred has an effect."""
    now = processor.time
    expected = now + .2
    state = {"complete": False}

    def check():
        """Check the test value."""
        state['complete'] = True
        assert processor.time >= expected

    ident = processor.defer(check, now + .1)
    assert processor.delay(ident, now + .2)
    while not state['complete']:

        processor()
