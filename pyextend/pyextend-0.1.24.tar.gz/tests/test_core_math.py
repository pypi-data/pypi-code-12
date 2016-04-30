# coding: utf-8


import pytest


def test_isprime():
    from pyextend.core.math import isprime

    assert isprime(0) is False
    assert isprime(1) is False
    assert isprime(2) is True
    assert isprime(3) is True
    assert isprime(4) is False
    assert isprime(5) is True
    assert isprime(6) is False
    assert isprime(7) is True
    assert isprime(8) is False
    assert isprime(9) is False
    assert isprime(10) is False
    assert isprime(11) is True

    assert len([x for x in map(isprime, range(0, 100)) if x is True]) == 25

if __name__ == '__main__':
    pytest.main(__file__)
