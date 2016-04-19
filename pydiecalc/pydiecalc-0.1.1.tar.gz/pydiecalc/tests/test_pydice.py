import math
import unittest2

from pydiecalc import CaughtRollParsingError
from pydiecalc import DEBUG_MAX
from pydiecalc import DEBUG_MIN
from pydiecalc import roll


class TestPyDice(unittest2.TestCase):

    def test_pass(self):
        self.assertTrue(True)

    def test_roll_one(self):
        result, rolls = roll('1d1')
        self.assertEqual(1, result)

    def test_assignment(self):
        result, rolls = roll('x = 2')
        self.assertEqual(2, result)
        result, rolls = roll('x')
        self.assertEqual(2, result)

    def test_unknown_variables(self):
        result, rolls = roll('z')
        self.assertEqual(0, result)

    def test_floats(self):
        result, rolls = roll('1.1')
        self.assertEqual(1.1, result)
        result, rolls = roll('5 / 2.0')
        self.assertEqual(2.5, result)

    def test_max_roll(self):
        result, rolls = roll('1d10', debug=DEBUG_MAX)
        self.assertEqual(10, result)

    def test_parse_error(self):
        with self.assertRaises(CaughtRollParsingError):
            roll('1d10 + $')

    def test_zero_sized_roll(self):
        result, rolls = roll('1d0', debug=DEBUG_MAX)
        self.assertEqual(0, result)

    def test_constants_pi(self):
        result, rolls = roll('PI', debug=DEBUG_MAX)
        self.assertEqual(math.pi, result)

    def test_constants_e(self):
        result, rolls = roll('e', debug=DEBUG_MAX)
        self.assertEqual(math.e, result)

    def test_min_roll(self):
        result, rolls = roll('1d100', debug=DEBUG_MIN)
        self.assertEqual(1, result)

    def tet_unary_eq(self):
        result, rolls = roll('-1')
        self.assertEqual(-1, result)
        result, rolls = roll('+1')
        self.assertEqual(1, result)

        result, rolls = roll('-1d100', debug=DEBUG_MIN)
        self.assertEqual(-1, result)

        result, rolls = roll('+1d100', debug=DEBUG_MIN)
        self.assertEqual(1, result)

    def test_binary_eq(self):
        result, rolls = roll('1+1')
        self.assertEqual(1 + 1, result)
        result, rolls = roll('1 + 1')
        self.assertEqual(1 + 1, result)

        result, rolls = roll('1-1')
        self.assertEqual(1 - 1, result)
        result, rolls = roll('1 - 1')
        self.assertEqual(1 - 1, result)

        result, rolls = roll('2*2')
        self.assertEqual(2 * 2, result)
        result, rolls = roll('2 * 2')
        self.assertEqual(2 * 2, result)

        result, rolls = roll('10/2')
        self.assertEqual(10 / 2, result)
        result, rolls = roll('10 / 2')
        self.assertEqual(10 / 2, result)

        result, rolls = roll('2^3')
        self.assertEqual(2 ** 3, result)
        result, rolls = roll('2 ^ 3')
        self.assertEqual(2 ** 3, result)

    def test_binary_with_roll(self):
        result, rolls = roll('1+1d6', debug=DEBUG_MAX)
        self.assertEqual(1 + 6, result)
        result, rolls = roll('1 + 1d6', debug=DEBUG_MAX)
        self.assertEqual(1 + 6, result)

    def test_ternary_with_roll(self):
        result, rolls = roll('1d10 + 1d6 + 1d20', debug=DEBUG_MAX)
        self.assertEqual(10 + 6 + 20, result)

    def test_ternary_with_multi_roll(self):
        result, rolls = roll('3d10 + 2d6 + 1d20', debug=DEBUG_MAX)
        self.assertEqual(3 * 10 + 2 * 6 + 20, result)

    def test_ternary_with_multi_roll_eq(self):
        result, rolls = roll('3d10 + 2d6 + 1d20 + 2', debug=DEBUG_MAX)
        self.assertEqual(3 * 10 + 2 * 6 + 20 + 2, result)

    def test_crazy_stuff(self):
        result, rolls = roll('1d10^2', debug=DEBUG_MAX)
        self.assertEqual(10 ** 2, result)

        result, rolls = roll('1d10d1d6', debug=DEBUG_MAX)
        self.assertEqual(10 * 6, result)

        result, rolls = roll('(5+2)d(3)', debug=DEBUG_MAX)
        self.assertEqual(7 * 3, result)
