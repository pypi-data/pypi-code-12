"""
Tests for `my_checker` module.
"""
from my_checker import check_math

class TestCheckMath(object):

    def test_addition(self):
        assert check_math(2 + 4, 6)

    def test_subtraction(self):
        assert check_math(4 - 2, 2)
