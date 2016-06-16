"""Test for nx_itertools.recipes.dotproduct"""
from nx_itertools.recipes import dotproduct


def test_normal():
    """Test dotproduct."""
    # dotproduct 3x3
    data1, data2 = iter([1, 2, 3]), iter([4, 5, 6])
    res = dotproduct(data1, data2)
    assert res == 1 * 4 + 2 * 5 + 3 * 6
    assert list(data1) == []
    assert list(data2) == []

    # dotproduct 3x5
    data1, data2 = iter([1, 2, 3]), iter([4, 5, 6, 7, 8])
    res = dotproduct(data1, data2)
    assert res == 1 * 4 + 2 * 5 + 3 * 6
    assert list(data1) == []
    assert list(data2) == [7, 8]       # doesn't consume extra in vec2

    # dotproduct 5x2
    data1, data2 = iter([1, 2, 3, 7, 8]), iter([4, 5, 6])
    res = dotproduct(data1, data2)
    assert res == 1 * 4 + 2 * 5 + 3 * 6
    assert list(data1) == [8] # doesn't consume extra in vec1 after vec2 is
                              # exhausted and single element is consumed in
                              # vec1
    assert list(data2) == []

    # dotproduct 3x0
    data1, data2 = iter([1, 2, 3]), ()
    res = dotproduct(data1, data2)
    assert res == 0
    assert list(data1) == [2, 3] # doesn't consume extra in vec1 after vec2 is
                                 # exhausted and single element is consumed in
                                 # vec1

    # dotproduct 0x3
    data1, data2 = (), iter([1, 2, 3])
    res = dotproduct(data1, data2)
    assert res == 0
    assert list(data2) == [1, 2, 3]    # doesn't consume extra in vec2

    # dotproduct 0x0
    data1, data2 = (), ()
    res = dotproduct(data1, data2)
    assert res == 0
