import sys

from codeviking.math.geom2d import V2, Tri2, ConvPoly2, RI


def test_length():
    u = V2(3, 4)
    assert (u.length == 5.0)


def test_equals():
    u = V2(3, 4)
    v = V2(3, 4)
    w = (3, 4)
    assert (u == v)
    assert (u == w)


def test_dot_product():
    u = V2(2, -3)
    v = V2(1, 7)
    assert (u @ v == 2 * 1 - 3 * 7)
    assert (u.dot(v) == 2 * 1 - 3 * 7)
    assert (v @ u == 2 * 1 - 3 * 7)
    assert (v.dot(u) == 2 * 1 - 3 * 7)


def test_dot_product_tuple():
    u = V2(2, -3)
    v = (1, 7)
    assert (u @ v == 2 * 1 - 3 * 7)
    assert (u.dot(v) == 2 * 1 - 3 * 7)


def test_sub():
    u = V2(2, -3)
    v = V2(1, 7)
    assert (u - v == V2(1, -10))


def test_sub_tuple():
    u = V2(2, -3)
    v = (1, 7)
    assert (u - v == (1, -10))


def test_scalar_mult():
    u = V2(2, -3)
    assert (u * 2 == V2(4, -6))
    assert (2 * u == V2(4, -6))


def test_scalar_div():
    u = V2(2, -3)
    assert (u / 2.0 == V2(1, -1.5))


def test_scalar_floordiv():
    u = V2(9, -3)
    assert (u // 2 == V2(4, -2))


def test_neg():
    u = V2(2, -3)
    assert -u == V2(-2, 3)


def test_RI():
    i = RI(-2, .83)
    assert -2.1 not in i
    assert -2.0 in i
    assert 0.8 in i
    assert 0.831 not in i


def test_tri():
    t = Tri2((0, 0), (1, 0), (0, 1))
    assert ((0.5, 0.8) not in t)
    assert ((0.8, 0.1) in t)
    assert ((0.5, 0.5) in t)
    assert ((1, 0) in t)
    assert ((0, 0) in t)
    assert ((0, 1) in t)
    assert ((1, 1) not in t)


def test_poly():
    q = ConvPoly2([(0, 0), (1, 0), (1, 2), (0, 1)])
    assert ((0.5, 0.8) in q)
    assert ((1.8, 0.1) not in q)
    assert ((1.5, 0.5) not in q)
    assert ((0, 0) in q)
    assert ((1, 0) in q)
    assert ((1, 2) in q)
    assert ((0, 1) in q)
