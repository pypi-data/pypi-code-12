import pytest
from collections import OrderedDict
from emitter import Emitter


# Testing each method of Emitter


# Testing the on() method


def test_on_10():
    """ Register a listener without credit. """
    emitter = Emitter()
    emitter.on("test", callable)

    assert callable in emitter.listeners("test")


def test_on_20():
    """ Listener must be callable. """
    emitter = Emitter()

    with pytest.raises(TypeError):
        emitter.on("test", False)


def test_on_30():
    """ Register a listener along with its credit. """
    emitter = Emitter()
    emitter.on("test", callable, 3)

    assert emitter.listeners("test")[callable] == 3


def test_on_40():
    """ The default credit value is -1. """
    emitter = Emitter()
    emitter.on("test", callable)

    assert emitter.listeners("test")[callable] == -1


def test_on_50():
    """ Negative credits are accepted, meaning infinity. """
    emitter = Emitter()
    emitter.on("test", callable, -10)

    assert emitter.listeners("test")[callable] == -10


def test_on_60():
    """ Each listener must have its own credit. """
    emitter = Emitter()
    emitter.on("test", callable, 10)
    emitter.on("test", str, 20)
    emitter.on("test", int, -10)

    assert emitter.listeners("test")[callable] == 10
    assert emitter.listeners("test")[str] == 20
    assert emitter.listeners("test")[int] == -10


def test_on_70():
    """ Multiple events can be registered. """
    emitter = Emitter()
    emitter.on("test1", callable)
    emitter.on("test2", str)

    assert callable in emitter.listeners("test1")
    assert str in emitter.listeners("test2")


def test_on_80():
    """ Each event have its own listeners. """
    emitter = Emitter()
    emitter.on("test1", callable)
    emitter.on("test2", str)

    assert str not in emitter.listeners("test1")
    assert callable not in emitter.listeners("test2")


def test_on_90():
    """ Max of calls for a listener can be set using the "credit" argument. """
    emitter = Emitter()
    l = []

    emitter.on("test", lambda: l.append(1), 2)

    emitter.emit("test")
    emitter.emit("test")
    emitter.emit("test")

    assert len(l) == 2


def test_on_100():
    """ When no "credit" specified, listener can be called infinitely. """
    emitter = Emitter()
    l = []

    emitter.on("test", lambda: l.append(1))

    emitter.emit("test")
    emitter.emit("test")
    emitter.emit("test")

    assert len(l) == 3


def test_on_110():
    """ Creating an event using False value. """
    emitter = Emitter()

    emitter.on(False, str)

    assert False in emitter.events()


# Testing the once() method


def test_once_10():
    """ The listener is called one time maximally. """
    emitter = Emitter()
    l = []

    emitter.once("test", lambda: l.append(1))

    emitter.emit("test")
    emitter.emit("test")

    assert len(l) == 1


# Testing the emit() method


def test_emit_10():
    """ Event data is passed to the listeners. """
    emitter = Emitter()
    params = []

    def func(param1, param2, unused=None, param3=None):
        params.append(param1)
        params.append(param2)
        params.append(unused)
        params.append(param3)

    emitter.on("test", func)

    emitter.emit("test", 10, 20, param3="hello")

    assert params == [10, 20, None, "hello"]


def test_emit_20():
    """ Check that the listeners are fired in the right order. """
    emitter = Emitter()

    l = []

    emitter.on("raccoon", lambda: l.append(1))
    emitter.on("raccoon", lambda: l.append(2))
    emitter.on("raccoon", lambda: l.append(3))

    emitter.emit("raccoon")

    assert l == [1, 2, 3]


def test_emit_30():
    """ Emit the False event. """
    emitter = Emitter()

    l = []
    emitter.on(False, lambda: l.append(1))
    emitter.emit(False)

    assert 1 in l


def test_emit_40():
    """ Negative credit listeners can be triggered infinitely. """
    emitter = Emitter()

    l = []

    emitter.on("event", lambda: l.append(1), -22)
    emitter.emit("event")
    emitter.emit("event")
    emitter.emit("event")

    assert len(l) == 3


# Testing the events() method


def test_events_10():
    """ When no events registered, events() returns an empty set. """
    emitter = Emitter()

    assert emitter.events() == set()


def test_events_20():
    """ events() returns a set containing all events. """
    emitter = Emitter()

    emitter.on("test1", callable)
    emitter.on("test2", callable)
    emitter.on("test3", callable)

    events = emitter.events()

    assert "test1" in events
    assert "test2" in events
    assert "test3" in events


def test_events_30():
    """ Using the False event. """
    emitter = Emitter()

    emitter.on(False, callable)

    assert False in emitter.events()


# Testing the listeners() method


def test_listeners_10():
    """ When passing an event that doesn't exists, returns an empty dict. """
    emitter = Emitter()

    assert emitter.listeners("unknown") == {}


def test_listeners_20():
    """
    When passing an event, returning all callbacks attached to this event.
    The response is an OrderedDict formatted like so:
    {
        callable_1: credit_1,
        callable_2: credit_2,
        ...
    }
    """
    emitter = Emitter()

    emitter.on("test", callable, 10)
    emitter.on("test", list, 42)

    listeners = emitter.listeners("test")

    assert isinstance(listeners, OrderedDict)

    assert listeners[callable] == 10
    assert listeners[list] == 42


def test_listeners_30():
    """ Check that the insertion order of the listeners is conserved. """
    emitter = Emitter()

    emitter.on("raccoon", bool)
    emitter.on("raccoon", callable)
    emitter.on("raccoon", dict)

    assert type(emitter.listeners("raccoon")) is OrderedDict

    listeners = list(emitter.listeners("raccoon"))

    assert listeners == [bool, callable, dict]


def test_listeners_40():
    """ Listeners insertion order should be conserved even after update. """
    emitter = Emitter()

    emitter.on("raccoon", bool)
    emitter.on("raccoon", callable, 10)
    emitter.on("raccoon", dict)

    # update callable, setting credit from 10 to -1 (infinity)
    emitter.on("raccoon", callable)

    # update bool, setting credit from infinity to 10
    emitter.on("raccoon", bool, 10)

    listeners = list(emitter.listeners("raccoon"))

    assert listeners == [bool, callable, dict]


def test_listeners_50():
    """ Check that even if no listeners, an OrderedDict is returned. """
    emitter = Emitter()

    assert type(emitter.listeners("unknown")) is OrderedDict


def test_listeners_60():
    """ Get the listeners for the False event. """
    emitter = Emitter()

    emitter.on(False, callable)

    assert callable in emitter.listeners(False)


# Testing the remove() method


def test_remove_10():
    """ Remove all the events. """
    emitter = Emitter()

    emitter.on("raccoon", callable)
    emitter.on("fox", callable)

    emitter.remove()

    assert emitter.events() == set()


def test_remove_20():
    """ Removing only a specified event. """
    emitter = Emitter()

    emitter.on("test", callable)
    emitter.on("test", str)

    emitter.on("raccoon", callable)
    emitter.on("raccoon", str)

    emitter.remove("test")

    assert emitter.listeners("test") == {}
    assert callable in emitter.listeners("raccoon")
    assert str in emitter.listeners("raccoon")


def test_remove_30():
    """ Removing a listener. """
    emitter = Emitter()

    emitter.on("test", callable)
    emitter.on("test", str)

    emitter.remove("test", callable)

    listeners = emitter.listeners("test")

    assert callable not in listeners
    assert str in listeners


def test_remove_40():
    """ Remove the False event. """
    emitter = Emitter()

    emitter.on(False, callable)

    assert False in emitter.events()

    emitter.remove(False)

    assert False not in emitter.events()


def test_remove_50():
    """ Remove a listener of the False event. """
    emitter = Emitter()

    emitter.on(False, callable)

    assert callable in emitter.listeners(False)

    emitter.remove(False, callable)

    assert callable not in emitter.listeners(False)
