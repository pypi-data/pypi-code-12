from __future__ import division, absolute_import, print_function

from numpy.testing import TestCase, run_module_suite, assert_array_equal
from f2py_ext import fib2

class TestFib2(TestCase):

    def test_fib(self):
        assert_array_equal(fib2.fib(6), [0, 1, 1, 2, 3, 5])

if __name__ == "__main__":
    run_module_suite()
