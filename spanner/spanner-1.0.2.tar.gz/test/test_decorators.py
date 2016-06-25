import unittest
import random
import inspect
from spanner.decorators import validate_args, singleton, memoize


class SingletonTestCase(unittest.TestCase):
    def test_same_id(self):
        @singleton
        class Foo(object):
            "I'm a docstring"
            pass

        self.assertEquals(id(Foo()), id(Foo()))
        self.assertEquals(inspect.getdoc(Foo), "I'm a docstring")


class MemoizedTestCase(unittest.TestCase):
    def test_memoize(self):
        @memoize
        def foo(bar):
            "I'm a docstring"
            return random.random()

        self.assertEquals(id(foo(3)), id(foo(3)))
        self.assertEquals(inspect.getdoc(foo), "I'm a docstring")


@validate_args(int, str, list, float)
def properly_decorated(a, b, c=[0], d=None):
    pass


@validate_args(int, str, list)
def improperly_decorated(a, b, c, d=None):
    pass


@validate_args(int)
def no_kwargs(a):
    pass


class DecoratorTestCase(unittest.TestCase):

    def test_correct_args(self):
        try:
            properly_decorated(1, '2', [3], 4.)
        except Exception as e:
            self.fail('Caught unexpected exception: ' + str(e))

    def test_incorrect_args(self):
        with self.assertRaises(Exception):
            properly_decorated('1', '2', [3], 4)

    def test_keyword_args(self):
        try:
            properly_decorated(1, '2', c=[3], d=4.)
        except Exception as e:
            self.fail('Caught unexpected exception: ' + str(e))

    def test_reordered_keyword_args(self):
        try:
            properly_decorated(1, '2', d=4., c=[3])
        except Exception as e:
            self.fail('Caught unexpected exception: ' + str(e))

    def test_not_all_args_specified(self):
        with self.assertRaises(Exception):
            properly_decorated(1)

    def test_not_all_types_specified(self):
        with self.assertRaises(Exception):
            improperly_decorated(1, '2', [3], 4.)

    def test_no_kwargs(self):
        try:
            no_kwargs(1)
        except Exception as e:
            self.fail('Caught unexpected exception: ' + str(e))
