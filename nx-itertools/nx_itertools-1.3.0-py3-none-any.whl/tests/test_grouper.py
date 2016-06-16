"""Test for nx_itertools.recipes.grouper"""
from nx_itertools.recipes import grouper


def test_normal():
    """Test grouper."""
    # grouper with multiple
    data = iter('ABCDEF')
    res = grouper(data, 2)
    assert next(res) == ('A', 'B')
    assert list(res) == [('C', 'D'), ('E', 'F')]
    assert list(data) == []

    # grouper with non-multiple
    data = iter('ABCDE')
    res = grouper(data, 2)
    assert next(res) == ('A', 'B')
    assert list(res) == [('C', 'D'), ('E', None)]
    assert list(data) == []

    # grouper with non-multiple but fillvalue used
    data = iter('ABCDE')
    res = grouper(data, 2, fillvalue='X')
    assert next(res) == ('A', 'B')
    assert list(res) == [('C', 'D'), ('E', 'X')]
    assert list(data) == []

    # grouper with empty
    data = ()
    res = grouper(data, 2)
    assert list(res) == []

    # grouper with 0 specified
    data = iter('ABCDE')
    res = grouper(data, 0)
    assert list(res) == []
    assert list(data) == ['A', 'B', 'C', 'D', 'E']


def test_normal_peek():
    """Test grouper with peeking at iterable."""
    # grouper with multiple but peek makes it non-multiple
    data = iter('ABCDEF')
    res = grouper(data, 2)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('D', 'E'), ('F', None)]
    assert list(data) == []

    # grouper with non-multiple but peek makes it multiple
    data = iter('ABCDE')
    res = grouper(data, 2)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('D', 'E')]
    assert list(data) == []

    # grouper with multiple but peek makes it non-multiple but fillvalue used
    data = iter('ABCDEF')
    res = grouper(data, 2, fillvalue='X')
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('D', 'E'), ('F', 'X')]
    assert list(data) == []


def test_oddity():
    """Test oddities of grouper."""
    # grouper with -1 specified
    data = iter('ABCDE')
    res = grouper(data, -1)
    assert list(res) == []
    assert list(data) == ['A', 'B', 'C', 'D', 'E']

    # grouper of empty with -1 specified
    data = ()
    res = grouper(data, -1)
    assert list(res) == []
