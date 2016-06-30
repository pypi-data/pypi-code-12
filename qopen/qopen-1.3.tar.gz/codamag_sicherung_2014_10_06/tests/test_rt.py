"""
Tests for rt module.
"""

# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import unittest

from codamag.rt import rt_3D_approx


class TestCase(unittest.TestCase):

    def test_rt_3D_approx(self):
        """Test 3 values of figure 2 of Paasschens (1997)"""
        # r, t, c, l, P, dP
        tests = [(2, 3, 1, 1, 0.04 / 4, 5e-4),  # r=2.0l, (3, 0.04)
                 # r=2.8l, (4, 0.03)
                 (2.8 * 2, 4.0, 2, 2, 0.03 / (2.8 * 2) ** 2 / 2, 2e-5),
                 (4, 1, 6, 1, 0.02 / 4 ** 2, 2e-4)]  # r=4.0l, (6, 0.02)
        for r, t, c, l, P, dP in tests:
            #print(r, t, c, l, P, rt_3D_approx(r, t, c, l), dP)
            self.assertLess(abs(rt_3D_approx(r, t, c, l) - P), dP)


if __name__ == '__main__':
    unittest.main()
