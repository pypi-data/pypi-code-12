"""Tests for nx_itertools.extra.multi_map"""
import pytest
from nx_itertools.extra import multi_map


SEQ = ['APPLE', 'AARDVARK', 'BANANA']


def test_normal():
    """Test multi_map with no default_dict."""
    # first char is key
    data = iter(SEQ)
    res = multi_map(lambda x: x[0], data)
    assert res == {'A': ['APPLE', 'AARDVARK'],
                   'B': ['BANANA']}
    assert list(data) == []
    with pytest.raises(KeyError):
        tmp = res['C']               # pylint: disable=unused-variable

    # second char is key
    data = iter(SEQ)
    res = multi_map(lambda x: x[1], data)
    assert res == {'P': ['APPLE'],
                   'A': ['AARDVARK', 'BANANA']}
    assert list(data) == []
    with pytest.raises(KeyError):
        tmp = res['C']               # pylint: disable=unused-variable

    # third char is key
    data = iter(SEQ)
    res = multi_map(lambda x: x[2], data)
    assert res == {'P': ['APPLE'],
                   'R': ['AARDVARK'],
                   'N': ['BANANA']}
    assert list(data) == []
    with pytest.raises(KeyError):
        tmp = res['C']               # pylint: disable=unused-variable

    # identity is key
    data = iter(SEQ)
    res = multi_map(lambda x: x, data)
    assert res == {'APPLE': ['APPLE'],
                   'AARDVARK': ['AARDVARK'],
                   'BANANA': ['BANANA']}
    assert list(data) == []
    with pytest.raises(KeyError):
        tmp = res['C']               # pylint: disable=unused-variable

    # fixed key
    data = iter(SEQ)
    res = multi_map(lambda x: 'B', data)
    assert res == {'B': ['APPLE', 'AARDVARK', 'BANANA']}
    assert list(data) == []
    with pytest.raises(KeyError):
        tmp = res['C']               # pylint: disable=unused-variable

    # empty
    data = ()
    res = multi_map(lambda x: x[0], data)
    assert res == {}
    with pytest.raises(KeyError):
        tmp = res['C']               # pylint: disable=unused-variable


def test_normal_defaultdict():
    """Test multi_map with default_dict."""
    # first char is key
    data = iter(SEQ)
    res = multi_map(lambda x: x[0], data, default_dict=True)
    assert res == {'A': ['APPLE', 'AARDVARK'],
                   'B': ['BANANA']}
    assert list(data) == []
    assert res['C'] == []

    # second char is key
    data = iter(SEQ)
    res = multi_map(lambda x: x[1], data, default_dict=True)
    assert res == {'P': ['APPLE'],
                   'A': ['AARDVARK', 'BANANA']}
    assert list(data) == []
    assert res['C'] == []

    # third char is key
    data = iter(SEQ)
    res = multi_map(lambda x: x[2], data, default_dict=True)
    assert res == {'P': ['APPLE'],
                   'R': ['AARDVARK'],
                   'N': ['BANANA']}
    assert list(data) == []
    assert res['C'] == []

    # identity is key
    data = iter(SEQ)
    res = multi_map(lambda x: x, data, default_dict=True)
    assert res == {'APPLE': ['APPLE'],
                   'AARDVARK': ['AARDVARK'],
                   'BANANA': ['BANANA']}
    assert list(data) == []
    assert res['C'] == []

    # fixed key
    data = iter(SEQ)
    res = multi_map(lambda x: 'B', data, default_dict=True)
    assert res == {'B': ['APPLE', 'AARDVARK', 'BANANA']}
    assert list(data) == []
    assert res['C'] == []

    # empty
    data = ()
    res = multi_map(lambda x: x[0], data, default_dict=True)
    assert res == {}
    assert res['C'] == []
