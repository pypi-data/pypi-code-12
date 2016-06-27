from pylib.misc import functions


def divide(a, b):
    return a / b


def square(a):
    return a**2


def obj_function(self):
    return self


class Temp(object):
    pass



def test_first():
    assert functions.first([1,3,5]) == 1
    assert functions.first([]) is None


def test_partial_left():
    forty_by = functions.partial_left(divide, 40)
    assert forty_by(4) == 10


def test_partial_right():
    by_four = functions.partial_right(divide, 4)
    assert by_four(40) == 10


def test_compose():
    sq_div = functions.compose(square, divide)
    assert sq_div(10, 2) == 25


def test_sequence():
    sq_div = functions.compose(square, divide)
    assert sq_div(10, 2) == 25


def test_once():
    sq_once = functions.once(square)
    assert sq_once(12) == 144
    assert sq_once(12) is None


def test_maybe1():
    my_sq = functions.maybe(square)
    assert my_sq(12) == 144
    assert my_sq() is None


def test_maybe2():
    my_sq = functions.maybe(square, lambda x: x > 5)
    assert my_sq(12) == 144
    assert my_sq(4) is None


def test_maybe3():
    my_div = functions.maybe(divide, lambda x: x > 5, 2)
    assert my_div(100, 20) == 5
    assert my_div(120, 4)is None


def test_bind():
    obj = Temp()
    b = functions.bind(obj_function, obj)
    assert b() == obj


def test_attach():
    obj = Temp()
    functions.attach_method(obj_function, obj, 'get')
    assert obj.get() == obj
