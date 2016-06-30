import math as m
import error as u


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
    # assert u.atan(x) == m.arctan(x.mean)


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

    assert (x+y).return_derivative(y) == 1
    assert (x-y).return_derivative(x) == 1
    assert (x*y).return_derivative(y) == x.mean
    assert (x/y).return_derivative(x) == 1/y.mean
    assert (x**y).return_derivative(x) == y.mean*x.mean**(y.mean-1)
    assert u.sin(x).return_derivative(x) == m.cos(x.mean)
    assert u.cos(x).return_derivative(x) == -m.sin(x.mean)
    assert u.tan(x).return_derivative(x) == m.cos(x.mean)**-2
    assert u.exp(x).return_derivative(x) == m.exp(x.mean)
