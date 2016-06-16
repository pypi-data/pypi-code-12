"""Tests for nx_itertools.extra.chunk"""
from nx_itertools.extra import chunk


def test_normal():
    """Test chunk."""
    # chunk with multiple
    data = iter('ABCDEFGH')
    res = chunk(data, 2)
    assert next(res) == ('A', 'B')
    assert list(res) == [('C', 'D'), ('E', 'F'), ('G', 'H')]
    assert list(data) == []

    # chunk with non-multiple
    data = iter('ABCDEFG')
    res = chunk(data, 2)
    assert next(res) == ('A', 'B')
    assert list(res) == [('C', 'D'), ('E', 'F'), ('G',)]
    assert list(data) == []

    # chunk with non-multiple
    data = iter('A')
    res = chunk(data, 2)
    assert next(res) == ('A',)
    assert list(res) == []
    assert list(data) == []

    # chunk empty
    data = ()
    res = chunk(data, 2)
    assert list(res) == []

    # chunk nothing
    data = iter('ABCDEFG')
    res = chunk(data, 0)
    assert list(res) == []
    assert list(data) == ['A', 'B', 'C', 'D', 'E', 'F', 'G']



def test_normal_peek():
    """Test chunk with peeking at iterable."""
    # chunk with multiple but peek makes it non-multiple
    data = iter('ABCDEFGH')
    res = chunk(data, 2)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('D', 'E'), ('F', 'G'), ('H',)]
    assert list(data) == []

    # chunk with non-multiple but peek makes it multiple
    data = iter('ABCDEFG')
    res = chunk(data, 2)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('D', 'E'), ('F', 'G')]
    assert list(data) == []

    # chunk with non-multiple but peek makes it multiple
    data = iter('ABC')
    res = chunk(data, 2)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == []
    assert list(data) == []


def test_oddity():
    """Test oddities of chunk."""
    # chunk negative does nothing
    data = iter('ABCDEFG')
    res = chunk(data, -1)
    assert list(res) == []
    assert list(data) == ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    # chunk negative does nothing
    data = ()
    res = chunk(data, -1)
    assert list(res) == []
