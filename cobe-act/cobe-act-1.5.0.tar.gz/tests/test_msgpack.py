"""Tests for the act._msgpack module.

The tests should use the public ``act.*`` API.

"""

import act


def test_mpack():
    data = act.mpack('hello world')
    assert isinstance(data, bytes)


def test_munpack():
    data = act.mpack(True)
    value = act.munpack(data)
    assert value is True


def test_unicode():
    data = act.mpack('unicode£€')
    value = act.munpack(data)
    assert isinstance(value, str)
    assert value == 'unicode£€'


def test_bytes():
    data = act.mpack(b'raw_bytes')
    value = act.munpack(data)
    assert isinstance(value, bytes)
    assert value == b'raw_bytes'
