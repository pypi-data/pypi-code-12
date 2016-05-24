# -*- coding: utf-8 -*-
"""
Test suite for the tinfiltering package.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

from unittest import TestCase
from tinfiltering.command_line import run_cmd


class TestConsole(TestCase):
    def test_basic(self):

        run_cmd()


class TestFilter(TestCase):

    def test_filtering(self):

        import tinfiltering
        import numpy as np

        test_data_1 = np.asarray([[1, 1], [2, 1], [2, 2], [1, 4], [1, 6],
                                  [10, 10]])
        test_data_2 = np.asarray([[1, 4], [1, 6], [2, 1], [2, 2], [1, 1]])

        test = tinfiltering.apply_filter(test_data_1[:, 0], test_data_1[:, 1])

        self.assertEqual(test_data_2.all(), test.all())
