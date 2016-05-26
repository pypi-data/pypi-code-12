import sys

from codeviking.math.geom2d import V2, Tri2, ConvPoly2, RI, Box2


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


def test_box2_expand():
    b = Box2((0, 1), (2, 3))
    assert b.expand((0.5, 2.4)) == b
    assert b.expand(Box2((0, 2), (-2, 1))) == Box2((0, 2), (-2, 3))


def test_box2_empty_expand():
    b = Box2.empty
    b.expand((0, 1)) == Box2((0, 1), (0, 1))


def test_box2_is_empty():
    b = Box2((0, 1), (2, 3))
    assert not b.is_empty
    assert Box2((1, -1), (1, -1)).is_empty
    assert Box2((1, -1), (1, 2)).is_empty
    assert Box2((1, 2), (1, -1)).is_empty
    assert Box2.empty.is_empty


def test_ri_expand():
    i = RI(0, 1)
    assert i.expand((0.5, 2.4)) == RI(0, 2.4)
    assert i.expand(5) == RI(0, 5)
    assert i.expand(0.1) == i


def test_ri_empty_expand():
    i = RI.empty
    i.expand((0, 1)) == RI(0, 1)
    i.expand(1) == RI(1, 1)


def test_ri_is_empty():
    i = RI(0, 1)
    assert not i.is_empty
    assert RI.empty.is_empty


def test_ri_intersects():
    a = RI(10, float('inf'))
    b = RI(float('-inf'), 20)
    c = RI(-1, 2)
    d = RI(0, 1)
    e = RI(4, 8)

    assert a.intersects(b)
    assert not a.intersects(c)
    assert not a.intersects(d)
    assert not a.intersects(e)
    assert b.intersects(c)
    assert b.intersects(d)
    assert b.intersects(e)
    assert c.intersects(d)
    assert not c.intersects(e)
    assert not d.intersects(e)


def test_ri_intersection():
    a = RI(10, float('inf'))
    b = RI(float('-inf'), 20)
    c = RI(-1, 2)
    d = RI(0, 1)
    e = RI(4, 8)

    assert a.intersection(b) == (10, 20)
    assert a.intersection(c).is_empty
    assert a.intersection(d).is_empty
    assert a.intersection(e).is_empty
    assert b.intersection(c) == c
    assert b.intersection(d) == d
    assert b.intersection(e) == e
    assert c.intersection(d) == (0, 1)
    assert c.intersection(e).is_empty
    assert d.intersection(e).is_empty
