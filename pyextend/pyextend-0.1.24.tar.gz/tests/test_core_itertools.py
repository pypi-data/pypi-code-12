# coding: utf-8
"""
    tests.test_core_itertools
    ~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.itertools  test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest


def test_unpack():
    from pyextend.core.itertools import unpack

    source = 'abc'
    a, b = unpack(source, 2)
    assert a == 'a' and b == 'b'

    a, b, c, d = unpack(source, 4, fill='-')
    assert a == 'a' and b == 'b' and c == 'c' and d == '-'

    source = ''
    a, b = unpack(source, 2)
    assert a is None and b is None

    a, b = unpack(source, 2, fill='')
    assert a == '' and b == ''

    source = ['a', 'b', 'c']
    a, b = unpack(source, 2)
    assert a == 'a' and b == 'b'

    a, b, c, d = unpack(source, 4, fill='')
    assert a == 'a' and b == 'b' and c == 'c' and d == ''

    with pytest.raises(TypeError):
        unpack(None, 2)


def test_merge():
    from pyextend.core.itertools import merge

    source = ['a', 'b', 'c']
    result = merge(source, [1, 2, 3])
    assert result == ['a', 'b', 'c', 1, 2, 3]

    result = merge(source, [1, 2, 3], ['x', 'y', 'z'])
    assert result == ['a', 'b', 'c', 1, 2, 3, 'x', 'y', 'z']

    source = 'abc'
    result = merge(source, '123')
    assert result == 'abc123'

    result = merge(source, '123', 'xyz')
    assert result == 'abc123xyz'

    source = ('a', 'b', 'c')
    result = merge(source, (1, 2, 3))
    assert result == ('a', 'b', 'c', 1, 2, 3)

    result = merge(source, (1, 2, 3), ('x', 'y', 'z'))
    assert result == ('a', 'b', 'c', 1, 2, 3, 'x', 'y', 'z')

    source = {'a': 1, 'b': 2, 'c': 3}
    result = merge(source, {'x': 'm', 'y': 'n'}, {'z': '1'})
    assert result == {'a': 1, 'b': 2, 'c': 3, 'x': 'm', 'y': 'n', 'z': '1'}

    with pytest.raises(TypeError):
        merge(None, 'abc')

if __name__ == '__main__':
    pytest.main(__file__)
