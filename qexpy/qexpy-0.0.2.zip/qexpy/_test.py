import error as u
import math as m


def test1():
    '''Test of elementary functions.
    '''
    x = u.Measurement(10, 1)

    assert u.sin(x) == m.sin(x.mean)
    assert u.cos(x) == m.cos(x.mean)
    assert u.tan(x) == m.tan(x.mean)
    assert u.csc(x) == 1/m.sin(x.mean)
    assert u.sec(x) == 1/m.cos(x.mean)
    assert u.cot(x) == 1/m.tan(x.mean)
    assert u.exp(x) == m.exp(x.mean)
    assert u.log(x) == m.log(x.mean)


def test2():
    '''Test of elementary operators.
    '''
    x = u.Measurement(10, 1)
    y = u.Measurement(20, 2)

    assert x+y == x.mean+y.mean
    assert x-y == x.mean-y.mean
    assert x*y == x.mean*y.mean
    assert x/y == x.mean/y.mean
    assert x**y == x.mean**y.mean


def test3():
    '''Test of derivative method.
    '''
    x = u.Measurement(3, 0.4)
    y = u.Measurement(12, 1)

    f = y**2*u.cos(x)-u.sin(x*y)
    fy = 2*y.mean*m.cos(x.mean) - m.cos(x.mean*y.mean)*x.mean
    fx = -y**2*m.sin(x.mean) - m.cos(x.mean*y.mean)*y.mean

    assert f.return_derivative(x) == fx
    assert f.return_derivative(y) == fy
