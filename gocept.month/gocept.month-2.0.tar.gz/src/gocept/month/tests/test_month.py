from .. import Month
import gocept.month.testing
import pytest


@pytest.fixture
def m():
    return Month(11, 2005)


@pytest.fixture(scope='module')
def zca(request):
    gocept.month.testing.setUpZCA()
    request.addfinalizer(gocept.month.testing.tearDownZCA)


class FakeMonth:
    month = 11
    year = 2005


fakemonth = FakeMonth()


def test_eq(m):
    assert m != None  # noqa
    assert m != fakemonth
    assert m == Month(11, 2005)
    assert m != Month(10, 2005)
    assert m != Month(11, 2004)


def test_lt(m):
    assert m < Month(11, 2006)
    assert m < Month(10, 2006)
    assert m < Month(12, 2005)
    assert not(m < Month(11, 2005))
    assert not(m < Month(10, 2005))
    assert not(m < Month(11, 2004))
    assert not(m < Month(12, 2004))
    with pytest.raises(TypeError):
        m < None
    with pytest.raises(TypeError):
        m < fakemonth


def test_gt(m):
    assert not(m > Month(11, 2006))
    assert not(m > Month(10, 2006))
    assert not(m > Month(12, 2005))
    assert not(m > Month(11, 2005))
    assert m > Month(10, 2005)
    assert m > Month(11, 2004)
    assert m > Month(12, 2004)
    with pytest.raises(TypeError):
        m > None
    with pytest.raises(TypeError):
        m > fakemonth


def test_le(m):
    assert m <= Month(11, 2006)
    assert m <= Month(10, 2006)
    assert m <= Month(12, 2005)
    assert m <= Month(11, 2005)
    assert not(m <= Month(10, 2005))
    assert not(m <= Month(11, 2004))
    assert not(m <= Month(12, 2004))
    with pytest.raises(TypeError):
        m <= None
    with pytest.raises(TypeError):
        m <= fakemonth


def test_ge(m):
    assert not(m >= Month(11, 2006))
    assert not(m >= Month(10, 2006))
    assert not(m >= Month(12, 2005))
    assert m >= Month(11, 2005)
    assert m >= Month(10, 2005)
    assert m >= Month(11, 2004)
    assert m >= Month(12, 2004)
    with pytest.raises(TypeError):
        m >= None
    with pytest.raises(TypeError):
        m >= fakemonth


def test_eq_str(m, zca):
    assert m == '11/2005'
    assert m != '10/2005'
    assert m != '11/2004'


def test_lt_str(m, zca):
    assert m < '11/2006'
    assert m < '10/2006'
    assert m < '12/2005'
    assert not(m < '11/2005')
    assert not(m < '10/2005')
    assert not(m < '11/2004')
    assert not(m < '12/2004')


def test_gt_str(m, zca):
    assert not(m > '11/2006')
    assert not(m > '10/2006')
    assert not(m > '12/2005')
    assert not(m > '11/2005')
    assert m > '10/2005'
    assert m > '11/2004'
    assert m > '12/2004'


def test_le_str(m, zca):
    assert m <= '11/2006'
    assert m <= '10/2006'
    assert m <= '12/2005'
    assert m <= '11/2005'
    assert not(m <= '10/2005')
    assert not(m <= '11/2004')
    assert not(m <= '12/2004')


def test_ge_str(m, zca):
    assert not(m >= '11/2006')
    assert not(m >= '10/2006')
    assert not(m >= '12/2005')
    assert m >= '11/2005'
    assert m >= '10/2005'
    assert m >= '11/2004'
    assert m >= '12/2004'


def test_eq_str_left(m, zca):
    assert '11/2005' == m
    assert '10/2005' != m
    assert '11/2004' != m


def test_lt_str_left(m, zca):
    assert '11/2006' > m
    assert '10/2006' > m
    assert '12/2005' > m
    assert not('11/2005' > m)
    assert not('10/2005' > m)
    assert not('11/2004' > m)
    assert not('12/2004' > m)


def test_gt_str_left(m, zca):
    assert not('11/2006' < m)
    assert not('10/2006' < m)
    assert not('12/2005' < m)
    assert not('11/2005' < m)
    assert '10/2005' < m
    assert '11/2004' < m
    assert '12/2004' < m


def test_le_str_left(m, zca):
    assert '11/2006' >= m
    assert '10/2006' >= m
    assert '12/2005' >= m
    assert '11/2005' >= m
    assert not('10/2005' >= m)
    assert not('11/2004' >= m)
    assert not('12/2004' >= m)


def test_ge_str_left(m, zca):
    assert not('11/2006' <= m)
    assert not('10/2006' <= m)
    assert not('12/2005' <= m)
    assert '11/2005' <= m
    assert '10/2005' <= m
    assert '11/2004' <= m
    assert '12/2004' <= m
