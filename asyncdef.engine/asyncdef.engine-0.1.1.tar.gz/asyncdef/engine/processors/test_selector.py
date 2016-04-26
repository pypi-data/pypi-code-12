"""Test suites for the ISelector processor implementation."""

import selectors

from asyncdef.interfaces.engine import iselector
import iface
import pytest

from . import selector as _selector


class StaticSelector:

    """Selector implementation for the tests."""

    def __init__(self):
        """Inititalize the event data store."""
        self.events = []
        self.listeners = {}

    def select(self, timeout=None):
        """Get all the events."""
        events, self.events = self.events, []
        return events

    def register(self, fd, events, data=None):
        """Register a listener."""
        if fd in self.listeners:

            raise KeyError()

        self.listeners[fd] = selectors.SelectorKey(fd, fd, events, data)
        return self.listeners[fd]

    def unregister(self, fd):
        """Unregister a listener."""
        if fd not in self.listeners:

            raise KeyError()

        self.listeners.pop(fd, None)

    def modify(self, fd, events, data):
        """Modify a listener."""
        self.unregister(fd)
        return self.register(fd, events, data)

    def get_key(self, fd):
        """Get a key."""
        key = self.listeners.get(fd, None)
        if not key:

            raise KeyError()

        return key


@pytest.fixture(scope='function')
def selector():
    """Get a test selector."""
    return StaticSelector()


@pytest.fixture(scope='function')
def processor(selector):
    """Get a test processor."""
    return _selector.Selector(selector=selector)


def test_file_implements_interface(processor):
    """Check if the implementation implements the interface."""
    assert iface.isinstance(processor, iselector.ISelector)


def test_file_adds_readers(selector, processor):
    """Check if the processor adds readers when asked."""
    processor.add_reader(1, lambda fd: None)
    assert selector.listeners[1]


def test_file_adds_readers_modifiy(selector, processor):
    """Check if the processor modifies if already watching."""
    sentinel = object()
    processor.add_reader(1, sentinel)
    processor.add_reader(1, None)
    assert selector.listeners[1].data[0] is None


def test_file_removes_readers(selector, processor):
    """Check if the processor removes readers when asked."""
    sentinel = object()
    processor.add_reader(1, sentinel)
    assert processor.remove_reader(1)
    assert 1 not in selector.listeners


def test_file_remove_readers_missing(selector, processor):
    """Check if remove_reader emits false when fd is not monitored."""
    assert not processor.remove_reader(1)


def test_file_removes_readers_modify(selector, processor):
    """Check if the processor removes readers with an active writer."""
    sentinel = object()
    processor.add_reader(1, sentinel)
    processor.add_writer(1, sentinel)
    assert processor.remove_reader(1)
    assert 1 in selector.listeners
    assert sentinel is selector.listeners[1].data[1]


def test_file_adds_writers(selector, processor):
    """CHeck if the processor adds writers when asked."""
    processor.add_writer(1, lambda fd: None)
    assert selector.listeners[1]


def test_file_adds_writers_modify(selector, processor):
    """Check if the processor modifies when already watching."""
    sentinel = object()
    processor.add_writer(1, sentinel)
    processor.add_writer(1, None)
    assert selector.listeners[1].data[1] is None


def test_file_remove_writers_missing(selector, processor):
    """Check if remove_writer emits false when fd is not monitored."""
    assert not processor.remove_writer(1)


def test_file_removes_writers(selector, processor):
    """Check if the processor removes writers when asked."""
    sentinel = object()
    processor.add_writer(1, sentinel)
    assert processor.remove_writer(1)
    assert 1 not in selector.listeners


def test_file_removes_writers_modify(selector, processor):
    """Check if the processor removes writers with an active reader."""
    sentinel = object()
    processor.add_reader(1, sentinel)
    processor.add_writer(1, sentinel)
    assert processor.remove_writer(1)
    assert 1 in selector.listeners
    assert sentinel is selector.listeners[1].data[0]


def test_file_triggers_read_only_events(selector, processor):
    """Check if the processor calls reader callbacks when reader."""
    state = {"fired": False}

    def fire(fd):
        """Flip the test bit."""
        state['fired'] = True

    processor.add_reader(1, fire)
    selector.events.append((
        selector.listeners[1],
        selectors.EVENT_READ,
    ))
    processor()
    assert state['fired'] is True


def test_file_triggers_write_only_events(selector, processor):
    """Check if the processor calls write callbacks when ready."""
    state = {"fired": False}

    def fire(fd):
        """Flip the test bit."""
        state['fired'] = True

    processor.add_writer(1, fire)
    selector.events.append((
        selector.listeners[1],
        selectors.EVENT_WRITE,
    ))
    processor()
    assert state['fired'] is True


def test_file_triggers_read_and_write_events(selector, processor):
    """Check if the processor calls both callbacks if ready."""
    state = {"fired": 0}

    def fire(fd):
        """Flip the test bit."""
        state['fired'] += 1

    processor.add_reader(1, fire)
    processor.add_writer(1, fire)
    selector.events.append((
        selector.listeners[1],
        selectors.EVENT_READ | selectors.EVENT_WRITE,
    ))
    processor()
    assert state['fired'] == 2
