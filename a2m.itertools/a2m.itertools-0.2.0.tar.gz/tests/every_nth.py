
import unittest
from a2m.itertools import every_nth


class NthFailureTestCase(unittest.TestCase):
    '''
    Test :py:func:`every_nth()` for failures.
    '''
    lst = range(20)

    def test_n_typeerror(self):
        '''``every_nth()`` raises a ``TypeError`` if called with non-integer ``n``.'''
        with self.assertRaises(TypeError) as cm:
            it = every_nth(self.lst, 'non-integer n', shift=0)
        self.assertEqual(cm.exception.args[0], 'n: an integer is required')

    def test_n_valueerror(self):
        '''``every_nth()`` raises a ``ValueError`` if called with zero or negative ``n``.'''
        with self.assertRaises(ValueError) as cm:
            it = every_nth(self.lst, -2, shift=1)
        self.assertEqual(cm.exception.args[0], 'n: a positive non-zero integer is required')

    def test_shift_typeerror(self):
        '''``every_nth()`` raises a ``TypeError`` if called with non-integer ``shift``.'''
        lst = range(20)
        with self.assertRaises(TypeError) as cm:
            it = every_nth(lst, 3, 'non-integer shift')
        self.assertEqual(cm.exception.args[0], 'shift: an integer is required')


class NthSuccessTestCase(unittest.TestCase):
    '''
    Success scenarios are covered with doctests.
    '''
    pass
