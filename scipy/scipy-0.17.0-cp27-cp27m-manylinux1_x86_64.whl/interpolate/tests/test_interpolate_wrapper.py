""" module to test interpolate_wrapper.py
"""
from __future__ import division, print_function, absolute_import

# Unit Test
import unittest
from numpy import arange, allclose, ones, isnan
import numpy as np

# functionality to be tested
from scipy.interpolate.interpolate_wrapper import (linear, logarithmic,
    block_average_above, nearest)


class Test(unittest.TestCase):

    def assertAllclose(self, x, y, rtol=1.0e-5):
        for i, xi in enumerate(x):
            self.assertTrue(allclose(xi, y[i], rtol) or (isnan(xi) and isnan(y[i])))

    def test_nearest(self):
        N = 5
        x = arange(N)
        y = arange(N)
        self.assertAllclose(y, nearest(x, y, x+.1))
        self.assertAllclose(y, nearest(x, y, x-.1))

    def test_linear(self):
        N = 3000.
        x = arange(N)
        y = arange(N)
        new_x = arange(N)+0.5
        new_y = linear(x, y, new_x)

        self.assertAllclose(new_y[:5], [0.5, 1.5, 2.5, 3.5, 4.5])

    def test_block_average_above(self):
        N = 3000
        x = arange(N, dtype=float)
        y = arange(N, dtype=float)

        new_x = arange(N // 2) * 2
        new_y = block_average_above(x, y, new_x)
        self.assertAllclose(new_y[:5], [0.0, 0.5, 2.5, 4.5, 6.5])

    def test_linear2(self):
        N = 3000
        x = arange(N, dtype=float)
        y = ones((100,N)) * arange(N)
        new_x = arange(N) + 0.5
        new_y = linear(x, y, new_x)
        self.assertAllclose(new_y[:5,:5],
                            [[0.5, 1.5, 2.5, 3.5, 4.5],
                             [0.5, 1.5, 2.5, 3.5, 4.5],
                             [0.5, 1.5, 2.5, 3.5, 4.5],
                             [0.5, 1.5, 2.5, 3.5, 4.5],
                             [0.5, 1.5, 2.5, 3.5, 4.5]])

    def test_logarithmic(self):
        N = 4000.
        x = arange(N)
        y = arange(N)
        new_x = arange(N)+0.5
        new_y = logarithmic(x, y, new_x)
        correct_y = [np.NaN, 1.41421356, 2.44948974, 3.46410162, 4.47213595]
        self.assertAllclose(new_y[:5], correct_y)

    def runTest(self):
        test_list = [name for name in dir(self) if name.find('test_') == 0]
        for test_name in test_list:
            exec("self.%s()" % test_name)

if __name__ == '__main__':
    unittest.main()
