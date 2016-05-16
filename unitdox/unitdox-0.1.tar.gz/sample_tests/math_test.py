# -*- coding: utf-8 -*-

import math
import unittest

from unitdox.__main__ import main

class MathTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_1_plus_1_equals_2(self):
        # Assign
        # Acts
        # Assert
        self.assertEqual(2, 1+1)

    def test_sqrt_of_a_negative_number_raise_a_ValueError_exception(self):
        # Assign
        # Acts
        try:
            math.sqrt(-1)
        except ValueError as exception:
            self.assertEqual('math domain error', exception.message)